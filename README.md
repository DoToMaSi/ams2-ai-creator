# AMS2 AI Creator

[![CI](https://github.com/USER/ams2-ai-creator/actions/workflows/ci.yml/badge.svg)](https://github.com/USER/ams2-ai-creator/actions/workflows/ci.yml)

Desktop tool for creating and managing **Automobilista 2 custom AI driver XML files**. Edit driver names, nationalities, and personality parameters with a visual editor, then save or export directly to your AMS2 installation.

## Overview

Automobilista 2 allows overriding AI driver names, personalities, and nationalities via XML files placed in:

```
{Steam AMS2 Folder}/UserData/CustomAIDrivers/
```

Each vehicle class uses its own file (for example `GT3.xml`, `StockCarV8.xml`, `F-Classic_Gen4.xml`). This application helps you:

- Create and edit custom AI XML files visually
- Work on **multiple XML files** at once via a left sidebar
- Use **Smart mode** (Skill + Aggression only) or **Custom mode** (full control)
- Apply **presets** (Junior → Master) with randomized realistic values
- Add **track-specific overrides** for the same livery
- Load existing community XML files and save/export them

Official AMS2 documentation: [Information for Customizing AI drivers in AMS2](https://forum.reizastudios.com/threads/information-for-customizing-ai-drivers-in-ams2.21758/)

---

## AMS2 Custom AI Context

### File naming

The XML filename must match the **vehicle class name** exactly (case-sensitive). Examples:

| Class | Filename |
|-------|----------|
| GT3 | `GT3.xml` |
| Stock Car V8 | `StockCarV8.xml` |
| Formula Classic Gen4 | `F-Classic_Gen4.xml` |

The app includes the full official class list in the **New File** dialog.

### Driver entries

Each `<driver>` element targets a **livery name** (case-sensitive, as shown in the AMS2 car selection screen):

```xml
<driver livery_name="Ministry Motorsport #51">
  <name>John Smith</name>
  <country>USA</country>
  <race_skill>0.75</race_skill>
</driver>
```

You can define **partial entries** — only specified fields override the default AI. Missing fields keep the game's original values.

### Track overrides

Multiple entries can share the same livery with a `tracks` attribute:

```xml
<driver livery_name="Ministry Motorsport #51" tracks="Azure_Circuit_2021,Long_Beach">
  <race_skill>0.99</race_skill>
</driver>
```

Fields not present in a track override inherit from the base driver entry for that livery.

---

## Parameter Reference

Most personality values range **0.0–1.0** in XML. The UI displays them as **0–100** for easier editing. Value **50** (~0.5) represents an average driver; extremes are valid but should be tested in-game.

| Parameter | UI Range | XML Range | Description |
|-----------|----------|-----------|-------------|
| `race_skill` | 0–100 | 0–1 | Race session skill (scaled by Opponent Skill Level) |
| `qualifying_skill` | 0–100 | 0–1 | Qualifying/practice skill (independent from race skill) |
| `wet_skill` | 0–100 | 0–1 | Wet track performance |
| `aggression` | 0–100 | 0–1 | Aggression (scaled by Opponent Aggression setting) |
| `defending` | 0–100 | 0–1 | Position defense intensity |
| `consistency` | 0–100 | 0–1 | Lap-to-lap skill variation |
| `stamina` | 0–100 | 0–1 | Fatigue resistance |
| `start_reactions` | 0–100 | 0–1 | Race start reaction speed |
| `tyre_management` | 0–100 | 0–1 | Tyre wear reduction |
| `fuel_management` | 0–100 | 0–1 | Fuel saving (ovals only for now) |
| `blue_flag_conceding` | 0–100 | 0–1 | Blue flag compliance |
| `weather_tyre_changes` | 0–100 | 0–1 | Tyre change likelihood in changing weather |
| `avoidance_of_mistakes` | 0–100 | 0–1 | General mistake avoidance |
| `avoidance_of_forced_mistakes` | 0–100 | 0–1 | Mistakes under defending pressure |
| `weight_scalar` | 90–110 | 0.900–1.100 | Vehicle mass multiplier (**also affects player** on that livery) |
| `power_scalar` | 90–110 | 0.900–1.100 | Engine power multiplier (**also affects player**) |
| `drag_scalar` | 90–110 | 0.900–1.100 | Aerodynamic drag multiplier (**also affects player**) |
| `setup_downforce` | 0–100 | 0–1 | Downforce preference (50 = neutral) |
| `setup_downforce_randomness` | 0–100 | 0–1 | Weekend setup variation |
| `vehicle_reliability` | 0–100+ | unbounded | Reliability ratio; values above 0.6 are generally good |

**Notes from Reiza:**
- `weight_scalar`, `power_scalar`, and `drag_scalar` affect the **player car** if you drive that livery
- `vehicle_reliability` can exceed 1.0; see the [forum post formula](https://forum.reizastudios.com/threads/information-for-customizing-ai-drivers-in-ams2.21758/) for class-specific reliability ranges
- Custom AI is **disabled in multiplayer**

---

## Smart vs Custom Modes

### Smart mode

Only **Race Skill** and **Aggression** are editable. All other parameters are **derived automatically** using correlations based on real community AI files (consistency, wet skill, tyre management, mistake avoidance, etc.).

Ideal for quickly creating believable drivers without tuning every slider.

### Custom mode

Every parameter is editable. Presets still randomize values, but nothing is auto-derived when you change skill or aggression.

---

## Presets

Click a preset button to randomize values within a skill tier:

| Preset | Skill (UI) | Aggression (UI) |
|--------|------------|-----------------|
| Junior | 5–22 | 15–35 |
| Amateur | 22–40 | 25–45 |
| Pro-Am | 40–58 | 30–55 |
| Pro | 58–75 | 35–65 |
| Elite | 75–90 | 40–72 |
| Master | 88–100 | 50–85 |

- **Smart + preset**: randomizes Skill/Aggression, then derives all other fields
- **Custom + preset**: randomizes all fields within tier-appropriate ranges

---

## Usage Guide

1. **Launch** the app (`python main.py` or `ams2-ai-creator`)
2. **New File** → pick a vehicle class filename (e.g. `GT3.xml`)
3. **+ Driver** → set livery name, driver name, and country
4. Choose **Smart** or **Custom** mode; adjust sliders or click a **preset**
5. Optionally **+ Override** to add track-specific values for the same livery
6. **Save** or **Save As** to write the XML file
7. **Export to AMS2** → select your `CustomAIDrivers` folder to copy the file in place
8. In AMS2, start an event with AI opponents ≤ number of customized drivers

Example files are included in [`docs/example_ai_files/`](docs/example_ai_files/) for reference.

---

## Installation

### From source (recommended for development)

Requirements: **Python 3.11+**

```bash
git clone https://github.com/USER/ams2-ai-creator.git
cd ams2-ai-creator
pip install -e ".[dev]"
python main.py
```

Or use the console entry point:

```bash
ams2-ai-creator
```

### Pre-built Windows release

Download `AMS2-AI-Creator-windows.zip` from:

- **[GitHub Releases](https://github.com/USER/ams2-ai-creator/releases)** after tagging `v*` on `master`
- **GitHub Actions artifacts** on the latest successful `master` push (CI workflow → `AMS2-AI-Creator-windows` artifact)

Extract and run `AMS2-AI-Creator.exe`.

---

## Development

### Project structure

```
ams2-ai-creator/
├── main.py                 # Entry point
├── ams2_ai/
│   ├── models/             # Driver/document models, parameter registry
│   ├── xml/                # XML reader/writer
│   ├── smart/              # Smart derivation + presets
│   ├── data/               # Vehicle classes, tracks, countries JSON
│   └── ui/                 # PySide6 interface
├── tests/
├── scripts/build_windows.ps1
├── scripts/build_windows.bat
└── .github/workflows/
```

### Commands

```bash
pip install -e ".[dev]"
pytest
ruff check .
ruff format .
```

### Debug logging

Set `AMS2_AI_DEBUG=1` for verbose console output:

```bash
# Windows PowerShell
$env:AMS2_AI_DEBUG=1; python main.py
```

---

## Build

Build a Windows distributable with PyInstaller:

```powershell
pip install -e ".[dev]"
./scripts/build_windows.ps1
```

Or on Windows Command Prompt:

```bat
pip install -e ".[dev]"
scripts\build_windows.bat
```

Output: `dist/AMS2-AI-Creator/` and `dist/AMS2-AI-Creator-windows.zip`

---

## CI/CD

### Branching

| Branch | Purpose | Pipelines |
|--------|---------|-----------|
| `develop` | Day-to-day development | None |
| `master` | Stable releases | CI on push/PR; Windows zip artifact on push; GitHub Release on version tags |

Workflow: commit on `develop` → open PR to `master` → CI runs on the PR → merge → tag `v*` on `master` for a release build.

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `ci.yml` | Push or PR to `master` | ruff lint, format check, pytest (Windows + Linux core tests); on push to `master`, PyInstaller build + zip artifact |
| `release.yml` | Tag `v*` on `master` | lint/test → PyInstaller build → GitHub Release zip |

---

## Logging & Troubleshooting

### Log file location

| Platform | Path |
|----------|------|
| Windows | `%APPDATA%\ams2-ai-creator\logs\ams2-ai-creator.log` |
| Linux/macOS | `~/.local/share/ams2-ai-creator/logs/ams2-ai-creator.log` |

Open the log folder from **Help → Open Log Folder** in the app.

Logs rotate at 5 MB (3 backups). Unhandled errors show a dialog with a **Copy Log Path** button.

### Common issues

| Problem | Solution |
|---------|----------|
| AI not appearing in-game | Verify filename matches vehicle class exactly; livery name is case-sensitive |
| Invalid XML on load | Check log for parse errors; validate against example files in `docs/example_ai_files/` |
| Scalar out of range | Weight/power/drag must be 0.900–1.100 in XML (90–110 in UI) |
| Export failed | Ensure AMS2 folder is writable; save the file first |
| Driver not customized | Set number of AI opponents ≤ number of customized drivers in the XML |

---

## License

MIT (placeholder — update as needed)

## Contributing

1. Branch from `develop` for new work.
2. Open pull requests into `master` when ready for review and release.
3. CI runs only on PRs targeting `master` — ensure checks pass before merge.
4. Create version tags (`v*`) on `master` to publish release artifacts.
