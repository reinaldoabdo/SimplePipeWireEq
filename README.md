# EM DESENVOLVIMENTO - NÃO USAR - PARA ESTUDO.

# SimplePipeWireEQ

Minimalist 10-band parametric equalizer for PipeWire on Linux.

## Features

- 10-band equalizer (-12dB to +12dB)
- Real-time audio adjustment
- Save/load custom presets
- GTK4 + Libadwaita UI
- Automatic first-run setup

## Requirements

- Linux with PipeWire
- pipewire >= 0.3.0
- pipewire-audio (or pipewire-pulse)
- Python >= 3.10
- GTK4 development libraries

Standard installation:
```bash
pip install .
```

For development (editable mode):
```bash
pip install -e .
simplepipewireq
```

Or run directly without installing:
```bash
PYTHONPATH=src python3 src/simplepipewireq/main.py
```

## Usage

Start the application and adjust the 10 frequency bands.
Changes apply in real-time to your audio output.

Save custom presets for quick access to favorite EQ settings.

## Troubleshooting

- PipeWire not running: `systemctl --user start pipewire`
- No audio changes: Check if pipewire-audio is installed
- Permission denied: Ensure ~/.config/pipewire/ is writable

## License

MIT
