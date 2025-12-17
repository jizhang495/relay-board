# Relay Board Control App

App to control a 8-channel USB-RLY08C relay board. It controls the on/off state of each channel. 

The programme uses Python, tkinter for GUI, and uv for package management.

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