# Eye-tracking hardware

> **Status:** drafted
> **Owner:** unassigned
> **Last reviewed:** 2026-06-01

## Tobii Pro Glasses 3

Wearable eye tracker. Two physical pieces:

- **Glasses** — head-worn unit with cameras, IR illuminators, scene camera, microphones.
- **Recording unit** — pocket-worn module holding the battery and SD card,
  connected to the glasses via an HDMI-style cable. Hosts the on-device Wi-Fi
  network used by the manager app.

<!-- TODO(unassigned): Fill exact model, firmware version, scene-camera resolution, IMU presence, sample rate of gaze. -->

| Field                  | Value |
|------------------------|-------|
| Model                  | Tobii Pro Glasses 3 |
| Firmware version       | TODO |
| Scene-camera resolution| TODO |
| Gaze sample rate       | TODO |
| Onboard storage        | SD card (capacity per unit: TODO) |
| Wireless               | 2.4 GHz Wi-Fi access point hosted by the recording unit |

## Wi-Fi network identification

Each unit broadcasts its own SSID in the format:

```
TG03B-XXXXXXXXXX
```

where the suffix is the unit's serial. The host PC running the manager joins
that network to control the unit.

<!-- TODO(unassigned): Track the lab's specific unit serials in your private lab manual / Joplin — do not commit them here (public repo). -->

## Default credentials

The Tobii factory default Wi-Fi password is **`TobiiGlasses`** (per Tobii's
publicly available device documentation).

> [!WARNING]
> **Change the Wi-Fi password before deploying** in any environment where
> nearby devices might join. The default password is public knowledge. If
> changing the password is not feasible per Tobii's procedure, treat the
> recording unit as having no Wi-Fi confidentiality and don't expose the unit
> beyond a controlled data-collection space.

<!-- TODO(unassigned): Document Tobii's procedure for rotating the on-unit Wi-Fi password, if supported by firmware. If not supported, note that explicitly. -->

## Maintenance

- Battery handling and swap interval: <!-- TODO -->
- SD card capacity and replacement cadence: <!-- TODO -->
- Lens cleaning and IR-illuminator window care: <!-- TODO -->
- Calibration target storage: <!-- TODO -->
