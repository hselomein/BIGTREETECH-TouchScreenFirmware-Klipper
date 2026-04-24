# `mainboard_port` — Configurable Mainboard Serial Port

## Purpose

The TFT has four physical UARTs labeled P1–P4. In the original firmware P1 is permanently hardwired as the mainboard port — all G-code goes out through it and all ACK responses are read back from it. P2/P3/P4 are "supplementary" ports used by remote hosts (OctoPrint, ESP3D, etc.).

The `mainboard_port` setting breaks that hardwiring. You can tell the TFT to treat any of the four ports as the mainboard port. The supplementary-port logic automatically skips whichever port you designate, so there is no cross-talk.

The main motivation is Klipper: Klipper's G-code interface lives on the Pi (as a virtual serial device), not on the MCU board. The TFT needs a UART wired to the Pi to talk to Klipper. Depending on how your printer is wired, that may already be P3 or P2 rather than P1.

---

## How It Works

Three code paths were changed:

| File | Change |
|---|---|
| `Mainboard_CmdHandler.c` | Outgoing G-codes are sent to `serialPort[mainboard_port - 1]` instead of the fixed P1 port |
| `Mainboard_AckHandler.c` | Incoming ACK responses are read from `serialPort[mainboard_port - 1]` instead of the fixed `SERIAL_PORT` constant |
| `SerialConnection.c` | `Serial_GetFromUART()` skips whichever port index is configured as mainboard — previously it always skipped P1; now it skips the configured port so a supplementary host on P2 cannot accidentally consume mainboard ACKs |

No other logic changes. The TFT still operates exactly the same way — it just uses the port you chose for all mainboard communication.

---

## Configuration

Two settings must be set consistently:

```ini
serial_port:P1:X P2:X P3:X P4:X   # baud rate per port (0 = off)
mainboard_port:N                    # which port is the mainboard (1–4)
```

The port selected by `mainboard_port` must be enabled with a non-zero baud rate in `serial_port`. All other ports can be enabled (for supplementary hosts) or disabled independently.

**Baud rate option values:**

| Value | Baud |
|---|---|
| 0 | OFF (disabled) |
| 6 | 115200 |
| 7 | 230400 |
| 8 | 250000 |
| 9 | 500000 |

---

## Configuration by Use Case

### Standard Marlin / RRF / Smoothieware

P1 is wired to the mainboard. No change from original behavior.

```ini
serial_port:P1:6 P2:0 P3:0 P4:0
mainboard_port:1
```

P2/P3/P4 can be enabled independently for OctoPrint or ESP3D without affecting this setting.

---

### Klipper — Production Wiring

The MCU board (e.g. SKR Mini E3) connects to the Pi over USB only. The Pi's GPIO UART is wired directly to TFT P1.

```
TFT P1  ──►  Pi /dev/ttyAMA0 (GPIO UART)
SKR Mini  ──►  Pi USB  (Klipper MCU firmware, silent on UART)
```

```ini
serial_port:P1:8 P2:0 P3:0 P4:0
mainboard_port:1
```

Baud rate `8` = 250000, which must match the `baud` value set for the serial section in `printer.cfg`:

```cfg
[mcu]
serial: /dev/ttyAMA0
baud: 250000
```

---

### Klipper — Testing Wiring (no disassembly required)

P1 is still wired to the MCU board (the original connection). P3 (or P2) is already wired to the Pi's GPIO UART because it was used as a supplementary serial for OctoPrint. You can test Klipper without touching any physical wiring by pointing `mainboard_port` at P3.

```
TFT P1  ──►  SKR Mini UART  (MCU board, silent — Klipper MCU firmware ignores G-code on this pin)
TFT P3  ──►  Pi /dev/ttyAMA0 (GPIO UART)
```

```ini
serial_port:P1:0 P2:0 P3:8 P4:0
mainboard_port:3
```

P1 is set to `0` (off) to prevent noise from the MCU board (which is running Klipper MCU firmware and will not respond to G-code). P3 is set to `8` (250000 baud) and designated as the mainboard port.

When you are ready for production, rewire P1 to the Pi, change `serial_port:P1:8`, and set `mainboard_port:1`.

---

### Klipper with OctoPrint/Mainsail on a Supplementary Port

If you want a remote host on P2 as well as Klipper on P1:

```ini
serial_port:P1:8 P2:6 P3:0 P4:0
mainboard_port:1
```

`Serial_GetFromUART` reads from P2 for the remote host and sends commands from P2 back to the TFT as if they came from a host. P1 is reserved for Klipper only and is skipped by the supplementary-port scan.

---

## What Stays the Same

- `serial_port` still controls the baud rate (and whether a port is active at all) for each port independently.
- Supplementary ports (OctoPrint, ESP3D) still work on whichever non-mainboard ports you enable.
- All four physical ports are still available — this setting only determines which one carries mainboard traffic.
- The setting persists in flash; changing `mainboard_port` in config.ini and re-flashing via SD card updates it like any other config value.

---

## Quick Reference

| Scenario | `serial_port` | `mainboard_port` |
|---|---|---|
| Marlin / RRF / Smoothieware (standard) | `P1:6 P2:0 P3:0 P4:0` | `1` |
| Klipper production (P1 → Pi) | `P1:8 P2:0 P3:0 P4:0` | `1` |
| Klipper testing (P3 → Pi, P1 → MCU) | `P1:0 P2:0 P3:8 P4:0` | `3` |
| Klipper testing via P2 | `P1:0 P2:8 P3:0 P4:0` | `2` |
| Marlin + OctoPrint on P2 | `P1:6 P2:6 P3:0 P4:0` | `1` |
