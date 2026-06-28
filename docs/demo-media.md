# Demo Media

The repository includes a short synthetic demo animation for GitHub:

- `docs/assets/demo-poster.png`
- `docs/assets/demo.gif`
- `docs/assets/demo.mp4`

The footage is generated from the real `dicom-dose-audit demo-bundle` command. It uses synthetic CT dose rows only and does not include DICOM files, protected health information, clinical conclusions, or regulatory determinations.

## Regenerate

```bash
python -m pip install -e ".[media]"
python scripts/generate_demo_media.py
```

The script writes a temporary bundle under `outputs/demo-media/`, extracts the bundle manifest, and renders the committed media files under `docs/assets/`.
