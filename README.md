# Digital Human Twin

Minimal Python/PySide6 base for a future digital human twin application.

## Goal

- Start with a clean desktop architecture
- Keep the codebase small
- Add future features inside `src/modules`

## Tech

- Python 3.10+
- PySide6 (Qt for Python)

## Chosen Direction (free-first)

- Chosen source: BodyParts3D
- Why: free anatomical dataset access suitable for prototyping layer-by-layer anatomy
- License note: BodyParts3D is published under CC BY-SA 2.1 JP; attribution/share-alike obligations apply

## Anatomy Ecosystem Options (market map)

### Open source / free

- 3D Slicer (BSD-style, open source, commercial use allowed): https://www.slicer.org/
- MITK Workbench (BSD, open source): https://www.mitk.org/
- ITK-SNAP (free and open source): https://www.itksnap.org/pmwiki/pmwiki.php
- Open Anatomy Project (free anatomy atlases/project): https://www.openanatomy.org/
- BodyParts3D (free dataset, CC BY-SA 2.1 JP): https://lifesciencedb.jp/bp3d/

### Commercial / paid

- Complete Anatomy (Elsevier): https://www.3d4medical.com/
- BioDigital Human (freemium + business plans): https://www.biodigital.com/
- Visible Body (education/professional licenses): https://www.visiblebody.com/
- Anatomage (premium real-cadaver ecosystem): https://www.anatomage.com/
- Materialise Mimics (clinical/engineering suite): https://www.materialise.com/en/healthcare/mimics-innovation-suite

## Structure

```text
src/
  app/
  core/
  assets/
  modules/
  main.py
```

## 3D Body Pipeline (implemented)

1. Import and prepare assets by layer:
- Local pipeline root at `src/assets/bodyparts3d/`
- Asset catalog and layer definitions in `src/core/anatomy_assets.py`

2. Map Skeleton/Fat/Muscle cards to anatomy layers:
- Mapping logic by mode/layer in `src/core/anatomy_assets.py`
- Runtime layer visibility tied to slider state

3. Keep UI and replace visual engine:
- Existing dashboard layout kept
- Body cards switched to Qt3D mesh rendering in `src/app/body_preview_widget.py`

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python src/main.py
```

## Current module capabilities

- Single active body per session (Neutral profile)
- Create/reset the active Neutral body
- Layer-by-layer anatomy exploration from skin to heart/arteries
- Dashboard view inspired by clinical twin layouts (Skeleton/Fat/Muscle + Scanned Organs + timeline)
- Provider abstraction ready for future real-asset integration (`src/core/anatomy_provider.py`)
- Qt3D mesh renderer for body cards (front / 3-quarter / side perspectives)
- BodyParts3D-first asset pipeline with layer-based rendering control

## Quick smoke test

```bash
python src/main.py --smoke-test
```
