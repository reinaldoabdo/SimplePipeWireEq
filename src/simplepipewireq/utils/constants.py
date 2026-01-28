import os
from pathlib import Path

# Frequencias dos 10 canais
FREQUENCIES = [60, 150, 400, 1000, 2500, 4000, 8000, 12000, 16000, 20000]

# Range de ganho
MIN_GAIN = -12.0
MAX_GAIN = 12.0
GAIN_STEP = 0.5

# Paths
HOME_DIR = Path.home()
CONFIG_DIR = HOME_DIR / ".config" / "pipewire"
PIPEWIRE_CONF_DIR = CONFIG_DIR / "pipewire.conf.d"
TEMP_CONF = CONFIG_DIR / "temp.conf"
PIPEWIRE_CONFIG_FILE = PIPEWIRE_CONF_DIR / "99-simplepipewireq.conf"

# Comandos
PIPEWIRE_RELOAD_CMD = ["systemctl", "--user", "restart", "pipewire"]
PIPEWIRE_STATUS_CMD = ["systemctl", "--user", "is-active", "pipewire"]

# UI
WINDOW_WIDTH = 770
WINDOW_HEIGHT = 600
APP_NAME = "SimplePipeWireEQ"
APP_VERSION = "1.0.0"
