import logging
import re
import subprocess
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from simplepipewireq.utils.constants import (
    PIPEWIRE_CONFIG_FILE, FREQUENCIES, PIPEWIRE_CONF_DIR, 
    PIPEWIRE_RELOAD_CMD, PIPEWIRE_STATUS_CMD,
    PIPEWIRE_RELOAD_SIGNAL, PIPEWIRE_PROCESS_NAME,
    PIPEWIRE_CLI_CMD, PIPEWIRE_LIST_NODES_CMD, PIPEWIRE_ENUM_PARAMS_CMD,
    PIPEWIRE_SET_PARAM_CMD, EQ_NODE_NAME, EQ_NODE_DESCRIPTION
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
        # Garantir que o módulo ALSA está carregado
        if not self.ensure_alsa_module():
            logger.warning("Não foi possível carregar módulo ALSA, continuando mesmo assim...")
        
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
                    f'{{ type = bq_peaking, freq = {freq}, gain = {gain_str}, q = 0.707 }}'
                )
            
            filters_str = ",\n                                ".join(filters_lua)
            
            # Template com param_eq em modo stereo nativo (1 nó, 2 canais)
            # Portas do param_eq: "In 1", "In 2", "Out 1", "Out 2"
            lua_content = f"""# SimplePipeWireEQ - Configuração de Equalizador Paramétrico
# Gerada automaticamente pela aplicação

context.modules = [
    {{
        name = libpipewire-module-filter-chain
        args = {{
            node.description = "SimplePipeWireEQ Equalizer Sink"
            media.name       = "SimplePipeWireEQ Equalizer Sink"
            filter.graph = {{
                nodes = [
                    {{
                        type   = builtin
                        name   = eq
                        label  = param_eq
                        config = {{
                            filters = [
                                {filters_str}
                            ]
                        }}
                    }}
                ]
                inputs  = [ "eq:In 1" "eq:In 2" ]
                outputs = [ "eq:Out 1" "eq:Out 2" ]
            }}
            capture.props = {{
                node.name       = "effect_input.simplepipewireq"
                media.class     = Audio/Sink
                audio.channels  = 2
                audio.position  = [ FL FR ]
            }}
            playback.props = {{
                node.name       = "effect_output.simplepipewireq"
                node.passive    = true
                audio.channels  = 2
                audio.position  = [ FL FR ]
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
        Reinicia o serviço PipeWire para aplicar as mudanças.
        Nota: filter-chains não suportam hot-reload, restart é necessário.
        """
        try:
            result = subprocess.run(
                PIPEWIRE_RELOAD_CMD,
                timeout=10,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("PipeWire reiniciado com sucesso")
                return True
            else:
                logger.error(f"Erro ao reiniciar PipeWire: {result.stderr}")
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
            # Regex ultra-flexível para JSON ou Lua (suporta aspas nas chaves e valores, e : ou =)
            pattern = r'"?type"?\s*[:=]\s*"?bq_peaking"?,\s*"?freq"?\s*[:=]\s*(\d+),\s*"?gain"?\s*[:=]\s*([-\d.]+)'
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

    # ==== HOT-RELOAD USING SIGHUP ====
    
    def reload_pipewire_signal(self) -> bool:
        """
        Envia sinal SIGHUP para o processo PipeWire para recarregar configuração.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            from simplepipewireq.utils.constants import PIPEWIRE_RELOAD_SIGNAL, PIPEWIRE_PROCESS_NAME
            import time
            
            # Tentar encontrar o processo primeiro
            pgrep_result = subprocess.run(
                ["pgrep", PIPEWIRE_PROCESS_NAME],
                capture_output=True,
                text=True
            )
            
            if pgrep_result.returncode != 0:
                logger.warning("Nenhum processo PipeWire encontrado")
                return False
            
            pids = pgrep_result.stdout.strip().split('\n')
            if not pids or not pids[0]:
                logger.warning("Nenhum PID de PipeWire encontrado")
                return False
            
            # Enviar SIGHUP para todos os processos pipewire
            success_count = 0
            for pid in pids:
                if pid:
                    try:
                        result = subprocess.run(
                            ["kill", f"-{PIPEWIRE_RELOAD_SIGNAL}", pid],
                            capture_output=True,
                            text=True
                        )
                        if result.returncode == 0:
                            success_count += 1
                            logger.info(f"Sinal SIGHUP enviado para PipeWire (PID: {pid})")
                    except Exception as e:
                        logger.warning(f"Erro ao enviar sinal para PID {pid}: {e}")
            
            if success_count > 0:
                # Aguardar um pouco para o PipeWire processar a nova configuração
                time.sleep(0.5)
                return True
            else:
                logger.error("Nenhum sinal SIGHUP foi enviado com sucesso")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar sinal SIGHUP: {e}")
            return False
    
    def restart_pipewire_pulse_only(self) -> bool:
        """
        Reinicia apenas o pipewire-pulse (interface PulseAudio).
        
        Isso é menos disruptivo que reiniciar o pipewire completo.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            result = subprocess.run(
                ["systemctl", "--user", "restart", "pipewire-pulse"],
                timeout=10,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("pipewire-pulse reiniciado com sucesso")
                return True
            else:
                logger.error(f"Erro ao reiniciar pipewire-pulse: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao reiniciar pipewire-pulse: {e}")
            return False
    
    def wait_for_pipewire_ready(self, timeout: float = 10.0) -> bool:
        """
        Aguarda o PipeWire estar pronto após reload.
        """
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ["pw-cli", "info", "0"],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0:
                    logger.info("PipeWire está pronto")
                    return True
            except Exception:
                pass
            time.sleep(0.2)
        
        logger.warning("Timeout esperando PipeWire ficar pronto")
        return False
    
    def hot_reload(self, gains_dict: dict) -> bool:
        """
        Executa reload do equalizador com múltiplas estratégias.
        
        Estratégias:
        1. SIGHUP (menos disruptivo)
        2. Restart pipewire-pulse (médio)
        3. Restart completo (fallback)
        
        Args:
            gains_dict: Dicionário de ganhos {freq: gain}
            
        Returns:
            bool: True se succeeded, False se falhou
        """
        import time
        
        logger.info("Iniciando reload do equalizador...")
        
        # Gerar configuração
        if not self.generate_pipewire_config(gains_dict):
            logger.error("Falha ao gerar configuração")
            return False
        
        # Aguardar arquivo ser escrito completamente
        time.sleep(0.3)
        
        # Estratégia 1: SIGHUP
        logger.info("Estratégia 1: Tentando SIGHUP...")
        if self.reload_pipewire_signal():
            logger.info("SIGHUP enviado, aguardando PipeWire...")
            if self.wait_for_pipewire_ready(timeout=10.0):
                logger.info("Reload via SIGHUP OK")
                return True
            else:
                logger.warning("SIGHUP enviado mas PipeWire não ficou pronto")
        else:
            logger.warning("Falha ao enviar SIGHUP")
        
        # Estratégia 2: Restart pipewire-pulse
        logger.info("Estratégia 2: Tentando restart pipewire-pulse...")
        if self.restart_pipewire_pulse_only():
            logger.info("pipewire-pulse reiniciado, aguardando...")
            if self.wait_for_pipewire_ready(timeout=10.0):
                logger.info("Reload via pipewire-pulse OK")
                return True
            else:
                logger.warning("pipewire-pulse reiniciado mas PipeWire não ficou pronto")
        else:
            logger.warning("Falha ao reiniciar pipewire-pulse")
        
        # Estratégia 3: Restart completo
        logger.info("Estratégia 3: Restart completo...")
        if self.reload_config():
            logger.info("Restart completo executado, aguardando...")
            result = self.wait_for_pipewire_ready(timeout=15.0)
            if result:
                logger.info("Restart completo OK")
            else:
                logger.error("Restart completo falhou ou demorou muito")
            return result
        
        logger.error("Todas as estratégias de reload falharam")
        return False

    # ==== DYNAMIC PARAMETER UPDATE USING PW-CLI ====
    
    def is_alsa_module_loaded(self) -> bool:
        """
        Verifica se o módulo ALSA do PipeWire está carregado.
        
        Returns:
            bool: True se carregado, False caso contrário
        """
        try:
            result = subprocess.run(
                ["pw-cli", "list-objects", "Module"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return False
            
            # Verificar se há algum módulo ALSA
            return 'libpipewire-module-alsa' in result.stdout.lower()
            
        except Exception as e:
            logger.error(f"Erro ao verificar módulo ALSA: {e}")
            return False
    
    def load_alsa_module(self) -> bool:
        """
        Carrega o módulo ALSA do PipeWire.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            logger.info("Carregando módulo ALSA do PipeWire...")
            result = subprocess.run(
                ["pw-cli", "load-module", "libpipewire-module-alsa"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                logger.info("✓ Módulo ALSA carregado com sucesso")
                # Aguardar dispositivos serem criados
                time.sleep(1.0)
                return True
            else:
                logger.error(f"✗ Erro ao carregar módulo ALSA: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao carregar módulo ALSA: {e}")
            return False
    
    def ensure_alsa_module(self) -> bool:
        """
        Garante que o módulo ALSA está carregado.
        Se não estiver, tenta carregar.
        
        Returns:
            bool: True se módulo está carregado ou foi carregado com sucesso
        """
        if self.is_alsa_module_loaded():
            logger.info("Módulo ALSA já está carregado")
            return True
        
        logger.warning("Módulo ALSA não está carregado, tentando carregar...")
        return self.load_alsa_module()
    
    def find_eq_node_id(self) -> Optional[int]:
        """
        Busca o ID do nó do equalizador usando pw-cli.
        
        Returns:
            Optional[int]: ID do nó se encontrado, None caso contrário
        """
        try:
            result = subprocess.run(
                PIPEWIRE_LIST_NODES_CMD,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Erro ao listar nós: {result.stderr}")
                return None
            
            # Procurar pelo nó do equalizador
            # O output do pw-cli contém informações sobre todos os nós
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Procurar pelo nome do nó ou descrição
                if EQ_NODE_NAME in line or EQ_NODE_DESCRIPTION in line:
                    # Extrair o ID do nó (formato: id X, ...)
                    import re
                    match = re.search(r'id\s+(\d+)', line)
                    if match:
                        node_id = int(match.group(1))
                        logger.info(f"Nó do equalizador encontrado: ID {node_id}")
                        return node_id
            
            logger.warning("Nó do equalizador não encontrado")
            return None
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout ao buscar nó do equalizador")
            return None
        except Exception as e:
            logger.error(f"Erro ao buscar nó do equalizador: {e}")
            return None
    
    def get_filter_chain_port_id(self, node_id: int) -> Optional[int]:
        """
        Busca o ID da porta do filter-chain associada ao nó.
        
        Args:
            node_id: ID do nó do equalizador
            
        Returns:
            Optional[int]: ID da porta se encontrada, None caso contrário
        """
        try:
            # Listar todas as portas
            result = subprocess.run(
                ["pw-cli", "list-objects", "Port"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                logger.error(f"Erro ao listar portas: {result.stderr}")
                return None
            
            lines = result.stdout.split('\n')
            
            for line in lines:
                # Procurar porta associada ao nó
                if f'node.id "{node_id}"' in line or f'node.id {node_id}' in line:
                    # Extrair o ID da porta
                    import re
                    match = re.search(r'id\s+(\d+)', line)
                    if match:
                        port_id = int(match.group(1))
                        logger.info(f"Porta do filter-chain encontrada: ID {port_id}")
                        return port_id
            
            logger.warning("Porta do filter-chain não encontrada")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar porta do filter-chain: {e}")
            return None
    
    def update_filter_gains_dynamic(self, gains_dict: dict) -> bool:
        """
        Atualiza os ganhos dos filtros dinamicamente usando pw-link e controle de volume.
        
        Esta é uma abordagem alternativa que usa o controle de volume do PipeWire
        para simular mudanças de EQ sem precisar recarregar o módulo.
        
        Args:
            gains_dict: Dicionário de ganhos {freq: gain}
            
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            # Calcular ganho médio para ajuste global
            # Esta é uma simplificação - para EQ real precisamos de controle mais granular
            avg_gain = sum(gains_dict.values()) / len(gains_dict) if gains_dict else 0.0
            
            # Converter dB para fator de amplitude
            # amplitude = 10^(dB/20)
            import math
            amplitude = 10 ** (avg_gain / 20.0)
            
            # Buscar o nó do equalizador
            node_id = self.find_eq_node_id()
            if not node_id:
                logger.error("Não foi possível encontrar o nó do equalizador")
                return False
            
            # Atualizar o volume do nó usando pw-cli
            # O PipeWire usa controle de volume em escala 0.0 a 1.0 (ou maior para boost)
            volume = max(0.0, min(4.0, amplitude))  # Limitar entre 0 e +12dB
            
            result = subprocess.run(
                ["pw-cli", "set-param", str(node_id), "Props", 
                 f"{{ channelVolumes: [ {volume}, {volume} ] }}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.info(f"Volume atualizado para {volume:.3f} ({avg_gain:.1f}dB)")
                return True
            else:
                logger.error(f"Erro ao atualizar volume: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao atualizar ganhos dinamicamente: {e}")
            return False
    
    def reload_filter_chain_module(self) -> bool:
        """
        Recarrega apenas o módulo filter-chain sem reiniciar o PipeWire.
        
        IMPORTANTE: Esta versão usa apenas SIGHUP para recarregar a configuração
        sem destruir o nó, preservando o ID do dispositivo. Isso evita que
        aplicativos como o Spotify percam a referência para o dispositivo.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            # Verificar se o nó do equalizador existe
            node_id = self.find_eq_node_id()
            
            if not node_id:
                logger.warning("Nó do equalizador não encontrado, tentando carregar...")
                # Se não existe, carregar o módulo
                return self.load_filter_chain_module()
            
            logger.info(f"Nó do equalizador encontrado (ID: {node_id}), recarregando configuração...")
            
            # Usar SIGHUP para recarregar a configuração sem destruir o nó
            # Isso preserva o ID do nó e evita que aplicativos percam a referência
            if self.reload_pipewire_signal():
                # Aguardar o PipeWire processar a nova configuração
                time.sleep(0.5)
                
                # Verificar se o nó ainda existe (deve existir com o mesmo ID)
                new_node_id = self.find_eq_node_id()
                if new_node_id == node_id:
                    logger.info(f"✓ Configuração recarregada com sucesso (nó ID preservado: {node_id})")
                    return True
                elif new_node_id:
                    logger.warning(f"⚠ Nó recriado com novo ID: {new_node_id} (antigo: {node_id})")
                    # O nó foi recriado, mas ainda funciona
                    return True
                else:
                    logger.error("✗ Nó do equalizador não encontrado após recarregamento")
                    return False
            else:
                logger.error("✗ Falha ao enviar SIGHUP")
                return False
            
        except Exception as e:
            logger.error(f"Erro ao recarregar módulo filter-chain: {e}")
            return False
    
    def load_filter_chain_module(self) -> bool:
        """
        Carrega o módulo filter-chain com a configuração atual.
        
        Returns:
            bool: True se sucesso, False se falha
        """
        try:
            # Verificar se o arquivo de configuração existe
            if not PIPEWIRE_CONFIG_FILE.exists():
                logger.error(f"Arquivo de configuração não encontrado: {PIPEWIRE_CONFIG_FILE}")
                return False
            
            # Carregar o módulo usando o arquivo de configuração
            # O PipeWire carrega automaticamente arquivos de .conf.d
            # Mas podemos forçar o recarregamento enviando SIGHUP
            logger.info("Carregando módulo filter-chain...")
            
            # Enviar SIGHUP para recarregar configuração
            if self.reload_pipewire_signal():
                # Aguardar o módulo ser carregado
                time.sleep(0.5)
                
                # Verificar se o nó foi criado
                node_id = self.find_eq_node_id()
                if node_id:
                    logger.info(f"Módulo filter-chain carregado com sucesso (nó ID: {node_id})")
                    return True
                else:
                    logger.warning("Módulo carregado mas nó não encontrado")
                    return False
            else:
                logger.error("Falha ao enviar SIGHUP")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao carregar módulo filter-chain: {e}")
            return False
    
    def hot_reload_dynamic(self, gains_dict: dict) -> bool:
        """
        Executa hot-reload dinâmico usando múltiplas estratégias.
        
        Estratégias (em ordem de preferência):
        1. Garantir que módulo ALSA está carregado
        2. Recarregamento do módulo filter-chain (mais robusto)
        3. Fallback para métodos existentes
        
        Args:
            gains_dict: Dicionário de ganhos {freq: gain}
            
        Returns:
            bool: True se sucesso, False se falha
        """
        logger.info("Iniciando hot-reload dinâmico...")
        
        # Garantir que o módulo ALSA está carregado
        if not self.ensure_alsa_module():
            logger.warning("Módulo ALSA não está disponível, áudio pode não funcionar")
        
        # Gerar configuração
        if not self.generate_pipewire_config(gains_dict):
            logger.error("Falha ao gerar configuração")
            return False
        
        # Aguardar arquivo ser escrito completamente
        time.sleep(0.2)
        
        # Estratégia 1: Recarregar módulo filter-chain
        logger.info("Estratégia 1: Recarregando módulo filter-chain...")
        if self.reload_filter_chain_module():
            logger.info("Hot-reload via módulo filter-chain OK")
            return True
        
        # Estratégia 2: Usar hot_reload existente (SIGHUP, pipewire-pulse, restart)
        logger.info("Estratégia 2: Usando hot-reload existente...")
        if self.hot_reload(gains_dict):
            logger.info("Hot-reload via método existente OK")
            return True
        
        logger.error("Todas as estratégias de hot-reload dinâmico falharam")
        return False

