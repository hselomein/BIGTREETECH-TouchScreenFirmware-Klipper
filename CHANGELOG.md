# Changelog — BIGTREETECH-TouchScreenFirmware-Klipper Fork

This document tracks changes made in this fork on top of the upstream
[bigtreetech/BIGTREETECH-TouchScreenFirmware](https://github.com/bigtreetech/BIGTREETECH-TouchScreenFirmware)
firmware. Upstream changes are not listed here; see the
[upstream releases](https://github.com/bigtreetech/BIGTREETECH-TouchScreenFirmware/releases)
for the full version history.

---

## [Unreleased] — post-merge additions

### Added
- `klipper/klipper_tft.cfg` — remote host print control protocol:
  - `_TFT_MONITOR` delayed_gcode polls `print_stats.state` every 3 s and sends
    `//action:print_start`, `//action:print_end`, `//action:pause`,
    `//action:resume`, `//action:cancel` to the TFT on state transitions
  - Progress bar updated via `//action:notification Data Left <pos>/<size>`
  - Remaining time updated via `//action:notification Time Left <h>h<m>m<s>s`
  - Layer counter updated via `//action:notification Layer Left <cur>/<total>`
    when slicer emits `SET_PRINT_STATS_INFO`
  - `M118` macro intercepts `M118 P0 A1 action:notification remote pause/resume/cancel`
    (TFT button presses in remote-host mode) and calls `PAUSE` / `RESUME` /
    `CANCEL_PRINT` in Klipper
- `klipper/mainboard_port.md` — reference doc for the `mainboard_port` config
  setting: purpose, how it works, configuration for all firmware types and
  wiring scenarios
- `klipper/remote_host.md` — reference doc for the remote host print-control
  protocol: feature overview, `//action:` message table, slicer setup for layer
  tracking (PrusaSlicer, Orca, SuperSlicer, Bambu Studio, Cura), timing, and
  debugging checklist
- `README.md` — Klipper Support appendix section with overview, required files
  table, wiring examples, and layer-tracking slicer setup

---

## [v28.x-klipper] — 2026-04-24

Merged upstream v28.x (`343afa9`) into our Klipper branch and added the initial
Klipper firmware support.

### Merged from upstream (v28.x)
- Added `TX_DELAY` config setting — minimum inter-command delay (ms) to the
  mainboard, helps prevent command corruption under ADVANCED_OK or high
  command rates
- Added `TX_PREFETCH` config setting — pre-fetches the next G-code from TFT
  media while the current one is in-flight, reducing SD read latency
- Added `COMMAND_CHECKSUM` documentation expanded with full protocol description
- Added `ADVANCED_OK` documentation expanded with TX_DELAY interaction notes
- Updated prebuilt binaries to v28.x for all supported TFT variants

### Added (Klipper support)
- `FW_KLIPPER` firmware type — TFT detects Klipper by reading
  `FIRMWARE_NAME:Klipper` in the M115 response and calls
  `setupMachine(FW_KLIPPER)`, which disables EEPROM-dependent operations
  (M503 stubbed, M420 S1 suppressed at boot, leveling set to ABL auto-detect)
- `mainboard_port` config setting (range 1–4, default 1) — redirects all
  mainboard serial communication (send and receive) from the hardwired P1 port
  to any of the four physical UARTs; enables testing Klipper via a supplementary
  UART already wired to the Pi without disassembling the screen
- `Serial_GetFromUART` updated to skip whichever port is configured as the
  mainboard port, preventing external-host data contention
- `CONFIG_FLASH_SIGN` and `PARA_SIGN` bumped to `20260424` to invalidate
  cached flash settings and force a re-read from config.ini on first boot
- `klipper/klipper_tft.cfg` — drop-in `printer.cfg` include providing:
  - `M115` — firmware identification in Marlin-compatible format for TFT
    detection (`FIRMWARE_NAME:Klipper`, capability flags)
  - `M105` — temperature reporting in `T:nnn /nnn B:nnn /nnn` format
  - `M114` — position reporting in Marlin `X:n Y:n Z:n E:n Count X:n ...` format
  - `M27` — print progress in `SD printing byte n/n` format
  - `M503` / `M501` / `M502` — EEPROM stubs (no-ops, respond `ok`)
  - `M500` — mapped to `SAVE_CONFIG`
  - `G29` — mapped to `BED_MESH_CALIBRATE`
  - `M420` — enable/disable bed mesh (`BED_MESH_PROFILE LOAD=default` / `BED_MESH_CLEAR`)
  - `M290` — babystep Z via `SET_GCODE_OFFSET Z_ADJUST`
  - `M851` — get/set probe Z offset via `SET_GCODE_OFFSET`
  - `M0` / `M1` / `M25` — mapped to `PAUSE`
  - `M24` — mapped to `RESUME`
  - `M524` — mapped to `CANCEL_PRINT`
  - `M600` — filament change pause with M117 notification
  - `M701` / `M702` — load/unload filament stubs (user-customizable)
  - `M303` — PID autotune via `PID_CALIBRATE`
  - `M900` — pressure advance via `SET_PRESSURE_ADVANCE`
  - `M201` / `M203` / `M204` / `M205` — velocity limits via `SET_VELOCITY_LIMIT`
  - `M108` / `M155` / `M211` / `M17` — misc stubs
- `klipper/config_klipper.ini` — pre-configured TFT SD card config file for
  Klipper users with annotated Klipper-specific notes on each setting;
  includes testing wiring defaults (`mainboard_port:3`, P3 at 250000 baud) and
  seven custom G-code buttons (home, bed mesh, restore mesh, save config,
  firmware restart, PID tune hotend)

---

## Credits

### Upstream Firmware

**[bigtreetech/BIGTREETECH-TouchScreenFirmware](https://github.com/bigtreetech/BIGTREETECH-TouchScreenFirmware)**
The original BTT TFT firmware this fork is based on. All core touch-mode UI,
serial communication, configuration, and hardware abstraction is their work.

**[neverhags/BIGTREETECH-TouchScreenFirmware-Klipper](https://github.com/neverhags/BIGTREETECH-TouchScreenFirmware-Klipper)**
The fork we branched from, which provided the starting point for adding Klipper
support to the BTT TFT firmware.

### Klipper Ecosystem

**[Klipper3d/klipper](https://github.com/Klipper3d/klipper)**
The 3D printer firmware this fork is designed to work with. The macro
compatibility layer in `klipper_tft.cfg` translates the TFT's Marlin-style
G-codes into Klipper equivalents.

**[Moonraker (arksine/moonraker)](https://github.com/Arksine/moonraker)**
Klipper's API server, used as the communication layer between the Pi and Klipper.
Referenced as the target platform for the bridge plugin that routes TFT serial
to Klipper's socket.

### Protocol Reference

**[jounathaen/octoprint_btt_touch_support](https://github.com/jounathaen/octoprint_btt_touch_support)**
The OctoPrint plugin that implements the BTT TFT host-action protocol
(`//action:print_start`, `//action:notification Time Left`, layer progress, and
remote pause/resume/cancel). The feature set and `//action:` message format
documented in that plugin were the specification used to implement the equivalent
functionality in `klipper_tft.cfg`.
