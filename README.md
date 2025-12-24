# PlatformIO Platform: ASR6601 (Ra-08-Kit) — WIP

> **Work in progress.** This is an experimental PlatformIO development platform for the **ASR6601 / Ai-Thinker Ra-08-Kit** modules, using the **Tremo SDK-style** build flow and a UART flasher integration.

## What this repo is
This repository provides a custom PlatformIO *platform* that:
- Builds Tremo-based projects with `arm-none-eabi-gcc`
- Generates `.elf` and `.bin`
- Adds a UART upload target using a `tremo_loader.py`-style flasher (compatible with the original workflow)

The original reference workflow (build + flash using `tremo_loader.py`) comes from Ai-Thinker’s public repository:
- https://github.com/Ai-Thinker-Open/Ai-Thinker-LoRaWAN-Ra-08

## Status
- ✅ Build works
- ✅ Upload works (UART bootloader mode)
- ✅ Basic examples run
- ⚠️ Still evolving: APIs, build flags, board definitions, and packaging will change.

## Quick start (example)
In a PlatformIO project:

```ini
[env:ra08]
platform = https://github.com/djpallax/platform-asr6601.git
board = ra08
framework = tremo

; Framework path (temporary)
; Option A (recommended): environment variable
; asr_framework_path = ${sysenv.ASR_FRAMEWORK_PATH}
; Option B: absolute path
asr_framework_path = /absolute/path/to/framework-asr6601

; Upload settings (set your port!)
upload_port = /dev/ttyUSB0
upload_speed = 921600

; Serial monitor
monitor_port  = ${this.upload_port}
monitor_speed = 115200
monitor_rts = 0
monitor_dtr = 0

; Optional features
use_printf = no
debug_uart = UART0

````
You can use Build, Upload and Serial Monitor buttons of PlatformIO, but if not, you can try:

Build:

```bash
pio run
```

Upload:

```bash
pio run -t upload
```

Serial monitor:

```bash
pio device monitor
```

## Configuration options

* `asr_framework_path`: Absolute path to the ASR/Tremo framework checkout used for includes, drivers, linker script, etc.
* `upload_port`: Serial port for flashing (e.g. `/dev/ttyUSB0`)
* `upload_speed`: Baudrate for flashing (e.g. `921600`)
* `monitor_*`: Standard PlatformIO monitor options
* `use_printf`: `yes/no` (enables the wrapped printf implementation if supported by the framework)
* `debug_uart`: `UART0/UART1/...` used as debug output UART selection

## Attribution / Third-party code and licensing

This project is based on (and in some places reuses/adapts) files and ideas from:

* Ai-Thinker Open: [https://github.com/Ai-Thinker-Open/Ai-Thinker-LoRaWAN-Ra-08](https://github.com/Ai-Thinker-Open/Ai-Thinker-LoRaWAN-Ra-08)

**Important note about licensing:** at the time of writing, the upstream repository does not appear to include a clear top-level `LICENSE` file. Because of that, I cannot confidently declare the license terms for upstream-derived files.

If you are the copyright holder or know the correct licensing terms, **please contact me** so I can:

* add proper attribution and licensing files, or
* refactor/remove any parts that cannot be redistributed.

## Disclaimer

This is not an official Ai-Thinker or ASR project. Use at your own risk.
