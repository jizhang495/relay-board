import tkinter as tk
from tkinter import messagebox, ttk
from typing import Iterable, List, Optional

import serial
from serial import SerialException
from serial.tools import list_ports


class RelayBoardController:
    """Simple wrapper around the USB-RLY08C serial protocol."""

    BAUDRATE = 19200
    GET_STATES_CMD = 91
    SET_STATES_CMD = 92

    def __init__(self) -> None:
        self._serial: Optional[serial.Serial] = None
        self.port: Optional[str] = None
        self.state: int = 0

    @staticmethod
    def available_ports() -> List[str]:
        return [port.device for port in list_ports.comports()]

    @property
    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def connect(self, port: str) -> int:
        self.close()
        try:
            self._serial = serial.Serial(
                port,
                baudrate=self.BAUDRATE,
                timeout=1,
                write_timeout=1,
            )
        except SerialException as exc:
            self._serial = None
            self.port = None
            raise exc

        self.port = port
        states = self.get_states()
        self.state = states if states is not None else 0
        return self.state

    def close(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()
        self._serial = None
        self.port = None

    def _ensure_connection(self) -> serial.Serial:
        if not self._serial or not self._serial.is_open:
            raise SerialException("Relay board is not connected.")
        return self._serial

    def _send_command(self, command: int, payload: bytes = b"", read_bytes: int = 0) -> bytes:
        ser = self._ensure_connection()
        ser.reset_input_buffer()
        ser.write(bytes([command]) + payload)
        if read_bytes:
            return ser.read(read_bytes)
        return b""

    def get_states(self) -> Optional[int]:
        response = self._send_command(self.GET_STATES_CMD, read_bytes=1)
        if response:
            self.state = response[0]
            return self.state
        return None

    def set_states(self, state: int) -> int:
        self._send_command(self.SET_STATES_CMD, bytes([state & 0xFF]))
        self.state = state & 0xFF
        return self.state

    def set_channel(self, channel: int, on: bool) -> int:
        if channel < 1 or channel > 8:
            raise ValueError("Channel must be between 1 and 8.")

        new_state = self.state | (1 << (channel - 1)) if on else self.state & ~(1 << (channel - 1))
        return self.set_states(new_state)

    def set_channels(self, channels: Iterable[int], on: bool) -> int:
        state = self.state
        for channel in channels:
            if channel < 1 or channel > 8:
                raise ValueError("Channel must be between 1 and 8.")
            state = state | (1 << (channel - 1)) if on else state & ~(1 << (channel - 1))
        return self.set_states(state)


class RelayBoardApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("USB-RLY08C Control")

        self.controller = RelayBoardController()

        self.port_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Disconnected")

        self.active_vars: List[tk.BooleanVar] = [tk.BooleanVar(value=True) for _ in range(8)]
        self.state_vars: List[tk.BooleanVar] = [tk.BooleanVar(value=False) for _ in range(8)]
        self.toggle_buttons: List[ttk.Button] = []

        self._build_ui()
        self.refresh_ports()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=10)
        main.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Connection controls.
        connection = ttk.LabelFrame(main, text="Connection", padding=10)
        connection.grid(row=0, column=0, sticky="ew")
        connection.columnconfigure(1, weight=1)

        ttk.Label(connection, text="COM Port:").grid(row=0, column=0, sticky="w")
        self.port_combo = ttk.Combobox(connection, textvariable=self.port_var, state="readonly")
        self.port_combo.grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ttk.Button(connection, text="Refresh", command=self.refresh_ports).grid(row=0, column=2, padx=(0, 5))
        self.connect_button = ttk.Button(connection, text="Connect", command=self.toggle_connection)
        self.connect_button.grid(row=0, column=3)

        ttk.Label(connection, textvariable=self.status_var).grid(row=1, column=0, columnspan=4, sticky="w", pady=(8, 0))

        # Relay controls.
        relays = ttk.LabelFrame(main, text="Relays", padding=10)
        relays.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        relays.columnconfigure(1, weight=1)

        for idx in range(8):
            row = idx // 2
            col_offset = (idx % 2) * 2

            active = ttk.Checkbutton(
                relays,
                text=f"Relay {idx + 1}",
                variable=self.active_vars[idx],
            )
            active.grid(row=row, column=col_offset, sticky="w", pady=4)

            btn = ttk.Button(
                relays,
                text=f"Relay {idx + 1}: OFF",
                command=lambda i=idx: self.toggle_relay(i + 1),
                width=18,
                state="disabled",
            )
            btn.grid(row=row, column=col_offset + 1, sticky="ew", pady=4, padx=(6, 0))
            self.toggle_buttons.append(btn)

        # Bulk actions.
        actions = ttk.Frame(main, padding=(0, 10, 0, 0))
        actions.grid(row=2, column=0, sticky="ew")
        ttk.Button(actions, text="Turn Selected On", command=lambda: self.set_selected(True), state="disabled").grid(
            row=0, column=0, sticky="ew"
        )
        ttk.Button(actions, text="Turn Selected Off", command=lambda: self.set_selected(False), state="disabled").grid(
            row=0, column=1, sticky="ew", padx=(8, 0)
        )
        ttk.Button(actions, text="Read States", command=self.refresh_states, state="disabled").grid(
            row=0, column=2, sticky="ew", padx=(8, 0)
        )
        self.bulk_buttons = actions.winfo_children()

    def refresh_ports(self) -> None:
        ports = self.controller.available_ports()
        current = self.port_var.get()
        self.port_combo["values"] = ports
        if ports and current not in ports:
            self.port_var.set(ports[0])
        elif not ports:
            self.port_var.set("")
        self.status_var.set(f"Found {len(ports)} port(s)." if ports else "No COM ports detected.")

    def toggle_connection(self) -> None:
        if self.controller.is_connected:
            self.controller.close()
            self.status_var.set("Disconnected")
            self.connect_button.config(text="Connect")
            self._set_controls_enabled(False)
            return

        port = self.port_var.get()
        if not port:
            messagebox.showinfo("Select Port", "Please choose a COM port to connect.")
            return

        try:
            state = self.controller.connect(port)
        except SerialException as exc:
            messagebox.showerror("Connection Failed", f"Could not open {port}.\n\n{exc}")
            self.status_var.set("Disconnected")
            return

        self.status_var.set(f"Connected to {port}")
        self.connect_button.config(text="Disconnect")
        self._set_controls_enabled(True)
        self._apply_state_to_ui(state)

    def refresh_states(self) -> None:
        if not self.controller.is_connected:
            messagebox.showinfo("Not connected", "Connect to a relay board first.")
            return
        try:
            state = self.controller.get_states()
        except SerialException as exc:
            messagebox.showerror("Read Failed", str(exc))
            return
        if state is None:
            messagebox.showwarning("No Response", "The relay board did not return any state data.")
            return
        self._apply_state_to_ui(state)

    def _set_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"
        for btn in self.toggle_buttons:
            btn.configure(state=state)
        for widget in self.bulk_buttons:
            widget.configure(state=state)

    def _apply_state_to_ui(self, state: int) -> None:
        for idx in range(8):
            bit_on = bool(state & (1 << idx))
            self.state_vars[idx].set(bit_on)
            label = f"Relay {idx + 1}: {'ON' if bit_on else 'OFF'}"
            self.toggle_buttons[idx].configure(text=label)

    def toggle_relay(self, channel: int) -> None:
        if not self.controller.is_connected:
            messagebox.showinfo("Not connected", "Connect to a relay board first.")
            return
        desired = not self.state_vars[channel - 1].get()
        try:
            state = self.controller.set_channel(channel, desired)
        except SerialException as exc:
            messagebox.showerror("Write Failed", str(exc))
            return
        self._apply_state_to_ui(state)

    def set_selected(self, on: bool) -> None:
        if not self.controller.is_connected:
            messagebox.showinfo("Not connected", "Connect to a relay board first.")
            return

        channels = [idx + 1 for idx, active in enumerate(self.active_vars) if active.get()]
        if not channels:
            messagebox.showinfo("No channels selected", "Tick at least one channel to control.")
            return

        try:
            state = self.controller.set_channels(channels, on)
        except SerialException as exc:
            messagebox.showerror("Write Failed", str(exc))
            return
        self._apply_state_to_ui(state)

    def on_close(self) -> None:
        self.controller.close()
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    app = RelayBoardApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
