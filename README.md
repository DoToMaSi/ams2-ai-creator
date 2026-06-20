# AMS2 AI Creator

[![CI](https://github.com/DoToMaSi/ams2-ai-creator/actions/workflows/ci.yml/badge.svg)](https://github.com/DoToMaSi/ams2-ai-creator/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/DoToMaSi/ams2-ai-creator?label=release)](https://github.com/DoToMaSi/ams2-ai-creator/releases)
[![License: MIT](https://img.shields.io/github/license/DoToMaSi/ams2-ai-creator)](https://github.com/DoToMaSi/ams2-ai-creator/blob/master/LICENSE)

**Version 1.0** — a desktop editor for **Automobilista 2 custom AI driver XML files**.

Create and tune AI opponents without hand-editing XML: driver names, countries, personality sliders, optional vehicle scalars, setup bias, per-track overrides, and more. Built for the AMS2 modding community by **[Douglas Tomacheski de Abreu e Silva (RockettSally)](https://github.com/DoToMaSi)**.

> **Repository:** [github.com/DoToMaSi/ams2-ai-creator](https://github.com/DoToMaSi/ams2-ai-creator)

---

## What it does

Automobilista 2 reads custom AI definitions from XML files in:

```
{Steam AMS2 Folder}/UserData/CustomAIDrivers/
```

Each **vehicle class** has its own file (for example `GT3.xml`, `StockCarV8.xml`, `F-Classic_Gen4.xml`). AMS2 AI Creator gives you a visual workflow to:

| Feature | Description |
|---------|-------------|
| **Multi-file editing** | Open several XML files at once; switch between them in the sidebar |
| **XML Properties** | Set display name, vehicle class, and optional custom filename per file |
| **Driver editor** | Livery name, driver name, country (with flags), Smart/Custom modes |
| **Smart mode** | Tune **Race Skill** + **Aggression**; other personality traits are derived automatically |
| **Custom mode** | Full manual control over every parameter |
| **Presets** | Junior → Master tiers with realistic randomized values |
| **Track overrides** | Per-track tabs for the same livery; searchable track picker grouped by venue |
| **Optional groups** | Vehicle Performance & Setup scalars — off by default, neutral defaults when unset |
| **Parameter help** | Every slider has a **?** icon explaining what it does and low vs high values |
| **Pretty XML** | Exported files are indented and readable; header comments carry file metadata |
| **Internal save** | **Save** validates and stores a snapshot in memory; **Export AI XML** writes the file |

Official AMS2 reference: [Information for Customizing AI drivers in AMS2](https://forum.reizastudios.com/threads/information-for-customizing-ai-drivers-in-ams2.21758/)

---

## Download (Windows)

No Python install required.

1. Download **`AMS2-AI-Creator-windows.zip`** from:
   - **[GitHub Releases](https://github.com/DoToMaSi/ams2-ai-creator/releases)** (recommended — versioned builds from `v*` tags)
   - **[GitHub Actions artifacts](https://github.com/DoToMaSi/ams2-ai-creator/actions/workflows/ci.yml)** on the latest successful `master` push (CI job **build-windows** → artifact `AMS2-AI-Creator-windows`)
2. Extract the zip.
3. Run **`AMS2-AI-Creator.exe`** inside the extracted folder (keep the `_internal` folder beside the exe).

Copy exported XML files into your AMS2 `CustomAIDrivers` folder, or use **File → Export to AMS2…** from the app.

---

## Quick start

1. **Launch** the app.
2. **+ New** or **+ Open** in the sidebar to create or load an XML file.
3. Expand **XML Properties** if you need to set the class name or custom filename.
4. **+ Driver** → enter livery name (exact in-game spelling), driver name, and country.
5. On the **Global** tab, choose **Smart** or **Custom**, adjust sliders or click a **preset**.
6. Optionally add **track override** tabs (+ on the tab bar) for venue-specific values.
7. **Save** to validate and mark the file clean in the editor.
8. **Export AI XML** to write the `.xml` file to disk.
9. **File → Export to AMS2…** to copy directly into your AMS2 `CustomAIDrivers` folder.
10. In AMS2, use **enough AI opponents** (≤ number of customized drivers in the file) for overrides to apply.

Example community files live in [`docs/example_ai_files/`](docs/example_ai_files/).

---

## AMS2 file format (essentials)

### Filename

Must match the **vehicle class** exactly (case-sensitive). The **New File** dialog includes the official class list; you can also use a **Custom…** filename for modded classes.

### Driver entry

Each `<driver>` targets a **livery name** (case-sensitive, as shown on the car select screen):

```xml
<driver livery_name="Ministry Motorsport #51">
  <name>John Smith</name>
  <country>USA</country>
  <race_skill>0.75</race_skill>
</driver>
```

Partial entries are supported — only specified fields override the default AI.

### Track overrides

Same livery, different track — use the `tracks` attribute:

```xml
<driver livery_name="Ministry Motorsport #51" tracks="Azure_Circuit_2021,Long_Beach">
  <race_skill>0.99</race_skill>
</driver>
```

Unset fields in a track override inherit from the base driver for that livery.

### Exported header comment

Each file includes structured metadata and attribution:

```xml
<!--
Name: My Season Pack
Class: GT3
Custom Name:
Created with the AMS2 AI Tool by RockettSally
-->
```

---

## Parameter reference

Most personality values are **0.0–1.0** in XML; the UI shows **0–100**. Value **50** (~0.5) is a typical average driver.

| Parameter | UI | XML | Notes |
|-----------|----|-----|-------|
| `race_skill` | 0–100 | 0–1 | Race skill; scaled by Opponent Skill Level in AMS2 |
| `qualifying_skill` | 0–100 | 0–1 | Qualifying/practice skill |
| `wet_skill` | 0–100 | 0–1 | Wet performance |
| `aggression` | 0–100 | 0–1 | Scaled by Opponent Aggression in AMS2 |
| `defending` | 0–100 | 0–1 | Defending intensity |
| `consistency` | 0–100 | 0–1 | Lap-to-lap variation |
| `stamina` | 0–100 | 0–1 | Fatigue resistance |
| `start_reactions` | 0–100 | 0–1 | Start reaction speed |
| `tyre_management` | 0–100 | 0–1 | Tyre wear |
| `fuel_management` | 0–100 | 0–1 | Fuel saving (ovals) |
| `blue_flag_conceding` | 0–100 | 0–1 | Blue flag compliance |
| `weather_tyre_changes` | 0–100 | 0–1 | Weather tyre strategy |
| `avoidance_of_mistakes` | 0–100 | 0–1 | General mistakes |
| `avoidance_of_forced_mistakes` | 0–100 | 0–1 | Mistakes under pressure |
| `weight_scalar` | 90–110 | 0.900–1.100 | Mass multiplier (**affects player** on that livery) |
| `power_scalar` | 90–110 | 0.900–1.100 | Power multiplier (**affects player**) |
| `drag_scalar` | 90–110 | 0.900–1.100 | Drag multiplier (**affects player**) |
| `setup_downforce` | 0–100 | 0–1 | Downforce bias (50 = neutral) |
| `setup_downforce_randomness` | 0–100 | 0–1 | Setup variation |
| `vehicle_reliability` | 0–100+ | float | Can exceed 1.0; see Reiza forum for class norms |

Hover or click **?** on any parameter row in the app for plain-language low/high guidance.

**Reiza notes:** scalars affect the player car on that livery; custom AI is **disabled in multiplayer**.

---

## Smart vs Custom

| | Smart | Custom |
|---|--------|--------|
| **Primary controls** | Race Skill, Aggression | All parameters |
| **Other personality fields** | Auto-derived from skill/aggression | Manual |
| **Vehicle / setup / reliability** | Editable when their optional groups are enabled | Same |
| **Best for** | Fast, believable drivers | Full control, unusual profiles |

Use the **?** beside the mode radios in the app for a short in-editor explanation.

---

## Presets

| Preset | Skill (UI) | Aggression (UI) |
|--------|------------|-----------------|
| Junior | 5–22 | 15–35 |
| Amateur | 22–40 | 25–45 |
| Pro-Am | 40–58 | 30–55 |
| Pro | 58–75 | 35–65 |
| Elite | 75–90 | 40–72 |
| Master | 88–100 | 50–85 |

- **Smart + preset:** randomizes skill/aggression, then derives the rest  
- **Custom + preset:** randomizes all fields within tier ranges  

---

## Install from source

Requirements: **Python 3.11+**, **Windows** recommended for the full GUI (Linux/macOS: core tests only in CI).

```bash
git clone https://github.com/DoToMaSi/ams2-ai-creator.git
cd ams2-ai-creator
pip install -e ".[dev,dev-gui]"
python main.py
```

Console entry point:

```bash
ams2-ai-creator
```

Debug logging:

```powershell
$env:AMS2_AI_DEBUG=1; python main.py
```

Logs: `%APPDATA%\ams2-ai-creator\logs\` (Windows) — or **Help → Open Log Folder**.

---

## Build locally

```powershell
pip install -e ".[dev]"
./scripts/build_windows.ps1
```

```bat
scripts\build_windows.bat
```

Output:

- `dist/AMS2-AI-Creator/` — runnable folder  
- `dist/AMS2-AI-Creator-windows.zip` — distributable archive  

---

## Development

```
ams2-ai-creator/
├── main.py
├── ams2_ai/
│   ├── models/          # Documents, drivers, parameters, header metadata
│   ├── xml/             # Reader / pretty-print writer
│   ├── smart/           # Smart derivation + presets
│   ├── identity/        # Name generation / romanization
│   ├── data/            # Classes, tracks, countries, flags
│   └── ui/              # PySide6 interface + AMS2 theme
├── assets/              # Icon, fonts
├── tests/
├── scripts/             # build_windows.*, build_icon.py, build_track_meta.py
└── .github/workflows/   # ci.yml, release.yml
```

```bash
pytest
ruff check .
ruff format .
```

---

## CI/CD

| Branch | Role |
|--------|------|
| `develop` | Day-to-day development |
| `master` | Stable line; CI on push/PR; Windows zip artifact on every push |

| Workflow | Trigger | Result |
|----------|---------|--------|
| [`ci.yml`](.github/workflows/ci.yml) | Push or PR → `master` | Lint, test, **Windows zip artifact** on push to `master` |
| [`release.yml`](.github/workflows/release.yml) | Tag `v*` on `master` | Lint, test, build, **GitHub Release** with zip |

Typical release flow: merge to `master` → tag `v1.0.0` (etc.) → Release workflow publishes the zip.

---

## Troubleshooting

| Problem | What to check |
|---------|----------------|
| AI not appearing in-game | Filename matches class exactly; livery name spelling/case |
| Overrides ignored | AI opponent count ≤ customized drivers in the XML |
| Invalid XML on load | See log; compare with `docs/example_ai_files/` |
| Scalar rejected | Weight/power/drag must be 0.900–1.100 in XML |
| Export failed | Save first; ensure target folder is writable |

---

## License & disclaimer

- **Source code:** [MIT License](LICENSE) — Copyright Douglas Tomacheski de Abreu e Silva (RockettSally)
- **Disclaimer:** This tool is **not affiliated with, endorsed by, or sponsored by** Reiza Studios or Automobilista 2. See **Help → Legal** in the app.

---

## Contributing

1. Branch from `develop`.
2. Open a pull request into `master`.
3. Ensure CI passes (lint, tests, Windows build on merge).
4. Tag `v*` on `master` for a public GitHub Release.

Issues and feature requests: [GitHub Issues](https://github.com/DoToMaSi/ams2-ai-creator/issues)
