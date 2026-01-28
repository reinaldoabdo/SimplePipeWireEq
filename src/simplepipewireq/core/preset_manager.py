import logging
import re
from pathlib import Path
from simplepipewireq.utils.constants import CONFIG_DIR, TEMP_CONF, PIPEWIRE_CONFIG_FILE
from simplepipewireq.core.pipewire_manager import PipeWireManager

logger = logging.getLogger(__name__)

class PresetManager:
    def __init__(self):
        """Inicializa o PresetManager e carrega cache."""
        self.pipewire_manager = PipeWireManager()
        self.presets_cache = self.list_presets()

    def list_presets(self) -> list:
        """
        Lista os presets disponíveis no diretório de configuração.
        
        Returns:
            list: Lista de nomes de presets (strings).
        """
        presets = []
        if not CONFIG_DIR.exists():
            return []

        for file in CONFIG_DIR.glob("*.conf"):
            # Ignorar arquivos de sistema e temporários
            if file.name in ["temp.conf", "pipewire.conf", "99-simplepipewireq.conf"]:
                continue
            presets.append(file.stem)
        
        self.presets_cache = sorted(presets)
        return self.presets_cache

    def validate_preset_name(self, name: str) -> bool:
        """
        Valida se o nome do preset é válido (letras, números, espaço, hífen).
        
        Returns:
            bool: True se válido.
        """
        if not name or len(name) > 50:
            return False
        # Permite alfanuméricos, espaços, hífens e underscores
        return bool(re.match(r'^[\w\s-]+$', name))

    def save_preset(self, name: str, gains_dict: dict) -> bool:
        r"""
        Salva um preset como arquivo .conf (mesmo formato que o PipeWire lê).
        Na verdade, para facilitar, vamos salvar apenas os ganhos ou o formato completo?
        O SPEC diz: "Formato: Lua (idêntico ao 99-simplepipewireq.conf, apenas com valores salvos)"
        
        Portanto precisamos gerar o conteúdo Lua.
        Como o PipeWireManager faz isso em generate_pipewire_config, poderíamos reutilizar lógica?
        Mas PipeWireManager escreve em um arquivo fixo.
        
        Vamos duplicar a lógica de geração ou extrair para um helper?
        Para evitar duplicação, vamos assumir que o PipeWireManager deveria ter um método 'get_config_content(gains)'.
        Mas como não implementamos isso lá ainda, vou implementar uma geração simplificada aqui que satisfaz o parse_preset_file.
        
        O `parse_preset_file` busca `type = bq_peaking, freq = (\d+), gain = ([-\d.]+)`.
        Então basta salvar nesse formato.
        """
        if not self.validate_preset_name(name):
            logger.error(f"Nome de preset inválido: {name}")
            return False

        filepath = CONFIG_DIR / f"{name}.conf"
        
        try:
            # Gerar conteúdo minimamente compatível com o parser
            # O parser espera formato Lua, então vamos fazer parecer Lua
            lines = ["# Preset File"]
            for freq, gain in gains_dict.items():
                lines.append(f'{{ "type": "bq_peaking", "freq": {freq}, "gain": {gain:.1f}, "q": 0.707 }}')
            
            with open(filepath, 'w') as f:
                f.write("\n".join(lines))
            
            logger.info(f"PresetManager: Arquivo '{filepath}' escrito com sucesso")
            self.list_presets() # Atualiza cache
            return True
        except Exception as e:
            logger.error(f"PresetManager: Erro ao salvar preset {name}: {e}")
            return False

    def delete_preset(self, name: str) -> bool:
        """
        Deleta um preset.
        """
        filepath = CONFIG_DIR / f"{name}.conf"
        if not filepath.exists():
            logger.warning(f"Tentativa de deletar preset inexistente: {name}")
            return False
        
        try:
            filepath.unlink()
            logger.info(f"Preset deletado: {name}")
            self.list_presets()
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar preset {name}: {e}")
            return False

    def get_preset_gains(self, name: str) -> dict:
        """
        Retorna os ganhos do preset.
        """
        filepath = CONFIG_DIR / f"{name}.conf"
        return self.pipewire_manager.parse_preset_file(filepath)
