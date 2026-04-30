# Relay Board Control App

App to control an 8-channel USB-RLY08C relay board. It includes both a Python desktop app and a browser-based Web Serial prototype.

## Python desktop app

The Python app uses Tkinter for the GUI and pyserial for serial communication.

### Using uv

1. Ensure [uv](https://docs.astral.sh/uv/) is installed.
2. Install dependencies: `uv sync`
3. Launch the app: `uv run python main.py`

### Using pip

1. Create and activate a virtual environment:
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
   - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Launch the app: `python main.py`

The app opens a Tkinter window. Pick the COM port for the USB-RLY08C, click **Connect**, tick the channels you want to act on, and use the per-channel toggle buttons or the **Turn Selected On/Off** buttons to drive the relays. Baud rate is set to 19200 as per the board datasheet.

Linux note: if Python was installed without Tkinter support, install your distro's Tk package, e.g. `sudo apt install python3-tk`.

### Python startup configuration

The initial ticked channels are read from `config.json` (shipped with all channels enabled). Edit `config.json` before launching to choose which channels should start ticked, e.g.:

```json
{
  "active_channels": [1, 2, 5, 6]
}
```

Changes you make to the tickboxes in the UI are saved back to `config.json` on the fly and when closing the app.

## Browser Web Serial prototype

The browser app is in `index.html`. It does not use Python for serial control; JavaScript talks directly to the board through the Web Serial API.

Use a Chromium-based browser such as Chrome or Edge.

1. Start a local static server:

   ```bash
   python3 -m http.server 8000
   ```

2. Open `http://localhost:8000`.
3. Click **Connect** and choose the USB-RLY08C serial port.

If port 8000 is already in use, choose another port and open that URL instead. Active relay selections are saved in the browser.

## Features

- serial connection to the relay board
- selection of active channels (tickboxes)
- on/off button for each channel
- on/off buttons for all selected channels
- relay state readback

## About USB-RLY08C

Datasheets of USB-RLY08C relay board can be found on: https://www.rapidonline.com/devantech-usb-rly08c-8-channel-2a-relay-board-controlled-via-usb-66-0338

The following commands are used:

| dec | hex | Action |
| --- | --- | --- |
| 56 | 38 | Get serial number - returns 8 bytes of ASCII that form the unique serial number for the module, e.g. "00001543". |
| 90 | 5A | Get software version - returns 2 bytes, the first being the Module ID (8), followed by the software version. |
| 91 | 5B | Get relay states - sends a single byte back to the controller; bit high means the corresponding relay is powered. |
| 92 | 5C | Set relay states - the next single byte will set all relay states; all on = 255 (11111111), all off = 0. |
| 100 | 64 | All relays on. |
| 101 | 65 | Turn relay 1 on. |
| 102 | 66 | Turn relay 2 on. |
| 103 | 67 | Turn relay 3 on. |
| 104 | 68 | Turn relay 4 on. |
| 105 | 69 | Turn relay 5 on. |
| 106 | 6A | Turn relay 6 on. |
| 107 | 6B | Turn relay 7 on. |
| 108 | 6C | Turn relay 8 on. |
| 110 | 6E | All relays off. |
| 111 | 6F | Turn relay 1 off. |
| 112 | 70 | Turn relay 2 off. |
| 113 | 71 | Turn relay 3 off. |
| 114 | 72 | Turn relay 4 off. |
| 115 | 73 | Turn relay 5 off. |
| 116 | 74 | Turn relay 6 off. |
| 117 | 75 | Turn relay 7 off. |
| 118 | 76 | Turn relay 8 off. |

According to the datasheet: 
> Most commands are only a single byte and if applicable the USB-RLY08-C will automatically send its response. The only exception to this being the "Set relay states" command which requires and additional desired states byte to be sent immediately after
the command byte.
