import configparser
import logging
from pathlib import Path
from simplepipewireq.utils.constants import TEMP_CONF, MIN_GAIN, MAX_GAIN, CONFIG_DIR

logger = logging.getLogger(__name__)

class ConfigManager:
    def __init__(self):
        """Inicializa o ConfigManager e garante que o diretório de configuração existe."""
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """Cria o diretório de configuração se não existir."""
        if not CONFIG_DIR.exists():
            try:
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                logger.info(f"Diretório de configuração criado: {CONFIG_DIR}")
            except OSError as e:
                logger.error(f"Erro ao criar diretório de configuração {CONFIG_DIR}: {e}")
                # Não levantamos erro aqui para não crashar na inicialização, 
                # mas operações de escrita falharão depois.

    def get_temp_config_path(self) -> Path:
        """Retorna o caminho do arquivo de configuração temporário."""
        return TEMP_CONF

    def validate_gain(self, value: float) -> bool:
        """Valida se o ganho está dentro do range permitido."""
        return MIN_GAIN <= value <= MAX_GAIN

    def write_config(self, filename: str, gains_dict: dict) -> bool:
        """
        Escreve o dicionário de ganhos em um arquivo .conf (formato INI).
        
        Args:
            filename: Nome do arquivo (ou caminho completo). 
                      Se não for absoluto, assume-se relativo a CONFIG_DIR.
            gains_dict: Dicionário {frequencia: ganho}
            
        Returns:
            bool: True se sucesso, False caso contrário.
        """
        try:
            filepath = self._resolve_path(filename)
            
            config = configparser.ConfigParser()
            config['equalizer'] = {}
            
            for freq, gain in gains_dict.items():
                if not self.validate_gain(gain):
                    logger.warning(f"Ganho inválido para {freq}Hz: {gain}. Ajustando para limites.")
                    gain = max(MIN_GAIN, min(gain, MAX_GAIN))
                
                # As chaves no INI serão gain_60hz, gain_150hz, etc.
                key = f"gain_{freq}hz"
                config['equalizer'][key] = str(float(gain))
            
            with open(filepath, 'w') as configfile:
                config.write(configfile)
                
            return True
            
        except Exception as e:
            logger.error(f"Erro ao escrever configuração em {filename}: {e}")
            return False

    def read_config(self, filename: str) -> dict:
        """
        Lê um arquivo .conf e retorna um dicionário de ganhos.
        
        Args:
            filename: Nome do arquivo (ou caminho completo).
            
        Returns:
            dict: {frequencia: ganho}. Retorna dict vazio se falhar.
        """
        try:
            filepath = self._resolve_path(filename)
            
            if not filepath.exists():
                logger.warning(f"Arquivo de configuração não encontrado: {filepath}")
                return {}
                
            config = configparser.ConfigParser()
            config.read(filepath)
            
            if 'equalizer' not in config:
                logger.warning(f"Seção [equalizer] não encontrada em {filepath}")
                return {}
            
            gains = {}
            for key, value in config['equalizer'].items():
                # Esperado formato: gain_60hz
                if key.startswith('gain_') and key.endswith('hz'):
                    try:
                        freq_str = key[5:-2] # remove "gain_" e "hz"
                        freq = int(freq_str)
                        gain = float(value)
                        
                        if self.validate_gain(gain):
                            gains[freq] = gain
                        else:
                             # Se inválido na leitura, clamp
                            gains[freq] = max(MIN_GAIN, min(gain, MAX_GAIN))
                            
                    except ValueError:
                        logger.warning(f"Erro ao parsear chave/valor: {key}={value}")
                        continue
            
            return gains
            
        except Exception as e:
            logger.error(f"Erro ao ler configuração de {filename}: {e}")
            return {}

    def _resolve_path(self, filename: str) -> Path:
        """Helper para resolver caminho absoluto ou relativo a CONFIG_DIR"""
        path = Path(filename)
        if path.is_absolute():
            return path
        return CONFIG_DIR / filename
