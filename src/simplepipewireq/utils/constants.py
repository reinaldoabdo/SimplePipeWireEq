import os
from pathlib import Path

# Frequencias dos 10 canais
FREQUENCIES = FREQUENCIES = [31, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

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

# Comandos para reload completo (fallback)
PIPEWIRE_RELOAD_CMD = ["systemctl", "--user", "restart", "pipewire"]
PIPEWIRE_STATUS_CMD = ["systemctl", "--user", "is-active", "pipewire"]

# Comandos para hot-reload usando SIGHUP (recomendado)
PIPEWIRE_RELOAD_SIGNAL = "HUP"  # Signal para recarregar config
PIPEWIRE_PROCESS_NAME = "pipewire"

# Comandos pw-cli para atualização dinâmica de parâmetros
PIPEWIRE_CLI_CMD = ["pw-cli"]
PIPEWIRE_LIST_NODES_CMD = ["pw-cli", "list-objects", "Node"]
PIPEWIRE_ENUM_PARAMS_CMD = ["pw-cli", "enum-params"]
PIPEWIRE_SET_PARAM_CMD = ["pw-cli", "set-param"]

# Nomes dos nós do equalizador
EQ_NODE_NAME = "effect_input.simplepipewireq"
EQ_NODE_DESCRIPTION = "SimplePipeWireEQ Equalizer Sink"

# IDs de controle para filtros param_eq
# O módulo filter-chain usa IDs específicos para cada parâmetro
CONTROL_ID_FILTER_GAIN = 1  # ID do parâmetro de ganho do filtro

# UI
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
APP_NAME = "SimplePipeWireEQ"
APP_VERSION = "1.0.0"
