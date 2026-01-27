import logging
import re
from pathlib import Path
from simplepipewireq.utils.constants import PIPEWIRE_CONFIG_FILE, FREQUENCIES, PIPEWIRE_CONF_DIR, PIPEWIRE_RELOAD_CMD

logger = logging.getLogger(__name__)

class PipeWireManager:
    def __init__(self):
        pass

    def is_configured(self) -> bool:
        """Verifica se arquivo de config foi criado."""
        return PIPEWIRE_CONFIG_FILE.exists()

    def setup_initial_config(self) -> bool:
        """Cria configuração inicial."""
        # TODO: Implementar
        return False

    def generate_pipewire_config(self, gains_dict: dict) -> bool:
        """Gera arquivo de configuração Lua para PipeWire."""
        # TODO: Implementar
        return False

    def reload_config(self) -> bool:
        """Recarrega PipeWire."""
        # TODO: Implementar
        return False

    def parse_preset_file(self, filepath: Path) -> dict:
        """
        Parse de arquivo Lua de preset para extrair ganhos.
        
        Args:
            filepath: Path ao arquivo .conf
        
        Returns:
            dict: {60: 0.5, 150: -1.0, ...}
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                logger.error(f"Arquivo não encontrado: {filepath}")
                return {}
            
            with open(filepath, 'r') as f:
                content = f.read()
            
            gains = {}
            # Regex para extrair frequência e ganho
            # Procura por: type = bq_peaking, freq = XXX, gain = YYY.Z
            pattern = r'type = bq_peaking, freq = (\d+), gain = ([-\d.]+)'
            matches = re.findall(pattern, content)
            
            if not matches:
                logger.warning(f"Nenhum filtro encontrado em {filepath}")
                return {}
            
            for freq_str, gain_str in matches:
                try:
                    freq = int(freq_str)
                    gain = float(gain_str)
                    gains[freq] = gain
                except ValueError as e:
                    logger.warning(f"Erro ao parsear freq={freq_str}, gain={gain_str}: {e}")
                    continue
            
            return gains
            
        except Exception as e:
            logger.error(f"Erro ao fazer parse de preset: {e}")
            return {}
