import logging
import re
import subprocess
from pathlib import Path
from simplepipewireq.utils.constants import (
    PIPEWIRE_CONFIG_FILE, FREQUENCIES, PIPEWIRE_CONF_DIR, 
    PIPEWIRE_RELOAD_CMD, PIPEWIRE_STATUS_CMD
)

logger = logging.getLogger(__name__)

class PipeWireManager:
    def __init__(self):
        pass

    def is_configured(self) -> bool:
        """Verifica se arquivo de config foi criado."""
        return PIPEWIRE_CONFIG_FILE.exists()

    def setup_initial_config(self) -> bool:
        """
        Cria configuração inicial (todos ganhos em 0dB) e recarrega PipeWire.
        Deve ser chamado na primeira inicialização da aplicação.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        # Criar ganhos padrão (todos em 0dB)
        default_gains = {freq: 0.0 for freq in FREQUENCIES}
        
        if not self.generate_pipewire_config(default_gains):
            logger.error("Falha ao gerar config inicial")
            return False
        
        if not self.reload_config():
            logger.error("Falha ao recarregar PipeWire após setup inicial")
            return False
        
        logger.info("Setup inicial do PipeWireEQ concluído com sucesso")
        return True

    def generate_pipewire_config(self, gains_dict: dict) -> bool:
        """
        Gera arquivo de configuração Lua para PipeWire.
        
        Args:
            gains_dict: Dict {freq: gain}
                       Ex: {60: 0.0, 150: 2.5, 400: -1.0, ...}
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            # Criar diretório se não existir
            PIPEWIRE_CONF_DIR.mkdir(parents=True, exist_ok=True)
            
            # Construir array de filtros
            filters_lua = []
            for freq in FREQUENCIES:
                gain = gains_dict.get(freq, 0.0)
                # Formatar ganho como float com 1 casa decimal
                gain_str = f"{gain:.1f}"
                filters_lua.append(
                    f'{{ type = "bq_peaking", freq = {freq}, gain = {gain_str}, q = 0.707 }}'
                )
            
            filters_str = ",\n                                ".join(filters_lua)
            
            # Template Lua (SPA-JSON format)
            lua_content = f"""// SimplePipeWireEQ - Configuração de Equalizador Paramétrico
// Gerada automaticamente pela aplicação

context.modules = [
    {{
        name = "libpipewire-module-filter-chain"
        args = {{
            node.description = "SimplePipeWireEQ Equalizer Sink"
            media.name = "SimplePipeWireEQ Equalizer Sink"
            filter.graph = {{
                nodes = [
                    {{
                        type = builtin
                        name = eq
                        label = param_eq
                        config = {{
                            filters = [
                                {filters_str}
                            ]
                        }}
                    }}
                ]
                links = []
            }}
            capture.props = {{
                node.name = "effect_input.simplepipewireq"
                media.class = "Audio/Sink"
                audio.channels = 2
                audio.position = [ FL FR ]
            }}
            playback.props = {{
                node.name = "effect_output.simplepipewireq"
                node.passive = true
                audio.channels = 2
                audio.position = [ FL FR ]
            }}
        }}
    }}
]
"""
            
            # Escrever arquivo
            with open(PIPEWIRE_CONFIG_FILE, 'w') as f:
                f.write(lua_content)
            
            logger.info(f"Arquivo PipeWire gerado: {PIPEWIRE_CONFIG_FILE}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao gerar config PipeWire: {e}")
            return False

    def reload_pipewire(self) -> bool:
        """
        Recarrega o serviço PipeWire para aplicar as mudanças.
        """
        try:
            # Previne o rate-limit do systemd dando reset no contador de falhas
            subprocess.run(["systemctl", "--user", "reset-failed", "pipewire.service"], check=False)
            
            result = subprocess.run(
                PIPEWIRE_RELOAD_CMD,
                timeout=5,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("PipeWire recarregado com sucesso")
                return True
            else:
                logger.error(f"Erro ao recarregar PipeWire: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Erro ao executar reload: {e}")
            return False

    def reload_config(self) -> bool:
        """Alias para compatibilidade."""
        return self.reload_pipewire()
    
    def is_pipewire_running(self) -> bool:
        """Verifica se PipeWire está rodando."""
        try:
            result = subprocess.run(
                PIPEWIRE_STATUS_CMD,
                timeout=2,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception:
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
            pattern = r'type = bq_peaking, freq = (\d+), gain = ([-\d.]+)'
            matches = re.findall(pattern, content)
            
            if not matches:
                # logger.warning(f"Nenhum filtro encontrado em {filepath}") # Silencioso é melhor as vezes
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
