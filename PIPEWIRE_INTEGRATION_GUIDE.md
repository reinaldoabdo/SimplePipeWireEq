# SimplePipeWireEQ - Guia de Integração com PipeWire

## Visão Geral

A aplicação SimplePipeWireEQ gera automaticamente arquivos de configuração Lua válidos para PipeWire que ativam um filtro-chain com equalizador paramétrico de 10 bandas.

Na **primeira execução**, a aplicação:
1. Verifica se `~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf` existe
2. Se não existe, cria com todos ganhos em 0dB
3. Executa `systemctl --user restart pipewire`
4. Mostra dialog confirmando sucesso

A cada **ajuste de slider**, a aplicação:
1. Atualiza o arquivo `99-simplepipewireq.conf` com novos valores
2. Recarrega PipeWire
3. User ouve a mudança em ~100-200ms

---

## Estrutura do Arquivo Lua Gerado

### Localização
```
~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
```

### Formato Completo

```lua
# SimplePipeWireEQ - Configuração de Equalizador Paramétrico
# Gerada automaticamente pela aplicação

context.modules = [
    {
        name = libpipewire-module-filter-chain
        args = {
            # Descrição e nome do nó
            node.description = "SimplePipeWireEQ Equalizer Sink"
            media.name = "SimplePipeWireEQ Equalizer Sink"
            
            # Grafo de filtros
            filter.graph = {
                nodes = [
                    {
                        type = builtin
                        name = eq
                        label = param_eq
                        config = {
                            filters = [
                                # Banda 1: 60 Hz
                                { type = bq_peaking, freq = 60, gain = 0.0, q = 0.707 },
                                # Banda 2: 150 Hz
                                { type = bq_peaking, freq = 150, gain = 0.0, q = 0.707 },
                                # Banda 3: 400 Hz
                                { type = bq_peaking, freq = 400, gain = 0.0, q = 0.707 },
                                # Banda 4: 1 kHz
                                { type = bq_peaking, freq = 1000, gain = 0.0, q = 0.707 },
                                # Banda 5: 2.5 kHz
                                { type = bq_peaking, freq = 2500, gain = 0.0, q = 0.707 },
                                # Banda 6: 4 kHz
                                { type = bq_peaking, freq = 4000, gain = 0.0, q = 0.707 },
                                # Banda 7: 8 kHz
                                { type = bq_peaking, freq = 8000, gain = 0.0, q = 0.707 },
                                # Banda 8: 12 kHz
                                { type = bq_peaking, freq = 12000, gain = 0.0, q = 0.707 },
                                # Banda 9: 16 kHz
                                { type = bq_peaking, freq = 16000, gain = 0.0, q = 0.707 },
                                # Banda 10: 20 kHz
                                { type = bq_peaking, freq = 20000, gain = 0.0, q = 0.707 }
                            ]
                        }
                    }
                ]
                links = []
            }
            
            # Propriedades de captura (entrada)
            capture.props = {
                node.name = "effect_input.simplepipewireq"
                media.class = "Audio/Sink"
                audio.channels = 2
                audio.position = [ FL FR ]
            }
            
            # Propriedades de reprodução (saída)
            playback.props = {
                node.name = "effect_output.simplepipewireq"
                node.passive = true
                audio.channels = 2
                audio.position = [ FL FR ]
            }
        }
    }
]
```

---

## Parâmetros dos Filtros Explicados

### type = bq_peaking
Tipo de filtro Butterworth biquad. `bq_peaking` é um filtro paramétrico (peaking EQ) que aumenta ou diminui ganho em uma frequência específica.

### freq
Frequência central em Hz (inteiro ou float).
- Valores: 20 - 20000 Hz
- Exemplo: `freq = 1000` = 1 kHz

### gain
Ganho em decibéis dB.
- Range: -12.0 a +12.0
- Negativo: reduz frequência
- Positivo: aumenta frequência
- Zero: sem alteração
- Exemplo: `gain = 2.5` = aumenta 2.5dB

### q
Fator Q - define a largura da banda de frequência.
- Valores comuns: 0.5 - 2.0
- Padrão: 0.707 (√2/2)
- Q alto: banda estreita, afeta frequência específica
- Q baixo: banda larga, afeta frequências próximas
- Para SimplePipeWireEQ: sempre 0.707

---

## Implementação em Python

### 1. Função: generate_pipewire_config()

Implementar em `src/simplepipewireq/core/pipewire_manager.py`:

```python
def generate_pipewire_config(self, gains_dict):
    """
    Gera arquivo de configuração Lua para PipeWire.
    
    Args:
        gains_dict: Dict {freq: gain}
                   Ex: {60: 0.0, 150: 2.5, 400: -1.0, ...}
    
    Returns:
        bool: True se sucesso, False se falha
        
    Raises:
        OSError: Se não conseguir escrever arquivo
        ValueError: Se gains_dict for inválido
    """
    import logging
    from pathlib import Path
    from simplepipewireq.utils.constants import (
        FREQUENCIES, PIPEWIRE_CONF_DIR, PIPEWIRE_CONFIG_FILE
    )
    
    logger = logging.getLogger(__name__)
    
    try:
        # Frequências em ordem
        frequencies = FREQUENCIES  # [60, 150, 400, 1000, 2500, 4000, 8000, 12000, 16000, 20000]
        
        # Criar diretório se não existir
        PIPEWIRE_CONF_DIR.mkdir(parents=True, exist_ok=True)
        
        # Construir array de filtros
        filters_lua = []
        for freq in frequencies:
            gain = gains_dict.get(freq, 0.0)
            # Formatar ganho como float com 1 casa decimal
            gain_str = f"{gain:.1f}"
            filters_lua.append(
                f"{{ type = bq_peaking, freq = {freq}, gain = {gain_str}, q = 0.707 }}"
            )
        
        filters_str = ",\n                                ".join(filters_lua)
        
        # Template Lua
        lua_content = f"""# SimplePipeWireEQ - Configuração de Equalizador Paramétrico
# Gerada automaticamente pela aplicação

context.modules = [
    {{
        name = libpipewire-module-filter-chain
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
```

### 2. Função: is_configured()

```python
def is_configured(self):
    """
    Verifica se arquivo de config foi criado.
    
    Returns:
        bool: True se arquivo existe, False caso contrário
    """
    from simplepipewireq.utils.constants import PIPEWIRE_CONFIG_FILE
    return PIPEWIRE_CONFIG_FILE.exists()
```

### 3. Função: setup_initial_config()

```python
def setup_initial_config(self):
    """
    Cria configuração inicial (todos ganhos em 0dB) e recarrega PipeWire.
    Deve ser chamado na primeira inicialização da aplicação.
    
    Returns:
        bool: True se sucesso, False se falha
    """
    import logging
    from simplepipewireq.utils.constants import FREQUENCIES
    
    logger = logging.getLogger(__name__)
    
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
```

### 4. Função: reload_config()

```python
def reload_config(self):
    """
    Recarrega PipeWire para aplicar novas configurações.
    
    Executa: systemctl --user restart pipewire
    
    Returns:
        bool: True se sucesso, False se falha
    """
    import subprocess
    import logging
    from simplepipewireq.utils.constants import PIPEWIRE_RELOAD_CMD
    
    logger = logging.getLogger(__name__)
    
    try:
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
            
    except subprocess.TimeoutExpired:
        logger.error("Timeout ao recarregar PipeWire (>5s)")
        return False
    except Exception as e:
        logger.error(f"Erro ao executar reload: {e}")
        return False
```

### 5. Função: parse_preset_file()

```python
def parse_preset_file(self, filepath):
    """
    Parse de arquivo Lua de preset para extrair ganhos.
    
    Args:
        filepath: Path ao arquivo .conf
    
    Returns:
        dict: {60: 0.5, 150: -1.0, ...}
        
    Raises:
        FileNotFoundError: Se arquivo não existe
        ValueError: Se arquivo não puder ser parseado
    """
    import re
    import logging
    from pathlib import Path
    
    logger = logging.getLogger(__name__)
    
    try:
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
        with open(filepath, 'r') as f:
            content = f.read()
        
        gains = {}
        
        # Regex para extrair frequência e ganho
        # Procura por: { type = bq_peaking, freq = XXX, gain = YYY.Z, q = 0.707 }
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
        
        logger.info(f"Parseado preset: {len(gains)} filtros")
        return gains
        
    except Exception as e:
        logger.error(f"Erro ao fazer parse de preset: {e}")
        raise
```

---

## Integração na Interface GTK

### main_window.py: on_slider_changed()

```python
def on_slider_changed(self, slider, band_index):
    """
    Callback quando slider de EQ é movido.
    
    Args:
        slider: O widget EQSlider
        band_index: Índice de 0-9 (qual frequência)
    """
    import threading
    from gi.repository import GLib
    
    # Obter novo valor
    new_gain = slider.get_value()
    frequency = FREQUENCIES[band_index]
    self.gains[frequency] = new_gain
    
    # Atualizar arquivo temp.conf (para referência)
    self.config_manager.write_config("temp.conf", self.gains)
    
    # Gerar arquivo PipeWire com novos valores
    if not self.pipewire_manager.generate_pipewire_config(self.gains):
        GLib.idle_add(self.update_status, "Erro ao atualizar config")
        return
    
    # Recarregar PipeWire em thread separada
    def reload_in_thread():
        success = self.pipewire_manager.reload_config()
        # Atualizar UI via idle_add (thread-safe)
        if success:
            GLib.idle_add(self.update_status, "Ajuste em tempo real...")
        else:
            GLib.idle_add(self.update_status, "Erro ao recarregar PipeWire")
    
    thread = threading.Thread(target=reload_in_thread, daemon=True)
    thread.start()
```

### main_window.py: on_load_preset()

```python
def on_load_preset(self, preset_name):
    """
    Carrega um preset salvo.
    
    Args:
        preset_name: Nome do preset (ex: "MeuRock")
    """
    import threading
    from gi.repository import GLib
    
    def load_in_thread():
        try:
            # Obter ganhos do preset
            gains = self.preset_manager.get_preset_gains(preset_name)
            
            # Atualizar ganhos em memória
            self.gains = gains
            
            # Gerar arquivo PipeWire
            if not self.pipewire_manager.generate_pipewire_config(gains):
                GLib.idle_add(self.update_status, "Erro ao gerar config")
                return
            
            # Recarregar PipeWire
            if not self.pipewire_manager.reload_config():
                GLib.idle_add(self.update_status, "Erro ao recarregar")
                return
            
            # Atualizar UI (sliders)
            GLib.idle_add(self._update_sliders_visual, gains)
            GLib.idle_add(self.update_status, f"Preset '{preset_name}' carregado")
            
        except Exception as e:
            GLib.idle_add(self.update_status, f"Erro ao carregar preset: {e}")
    
    thread = threading.Thread(target=load_in_thread, daemon=True)
    thread.start()

def _update_sliders_visual(self, gains):
    """Atualiza visualmente todos os sliders (deve ser chamado via idle_add)"""
    for i, slider in enumerate(self.sliders):
        frequency = FREQUENCIES[i]
        slider.set_value(gains.get(frequency, 0.0))
```

---

## Requisitos do Sistema

### Verificar Disponibilidade de filter-chain

```bash
pw-cli dump 0 core | grep filter-chain
```

Se não aparecer nada, pode ser necessário instalar módulos:

```bash
# Debian/Ubuntu
sudo apt install pipewire-audio pipewire-alsa pipewire-pulse

# Fedora
sudo dnf install pipewire-audio

# Arch
sudo pacman -S pipewire-audio
```

### Verificar PipeWire Rodando

```bash
systemctl --user is-active pipewire
systemctl --user is-active pipewire-pulse
```

Se não estiver rodando:

```bash
systemctl --user start pipewire
systemctl --user start pipewire-pulse
```

---

## Troubleshooting

### Problema: Erro "libpipewire-module-filter-chain not found"

**Solução:**
```bash
sudo apt install pipewire-audio
systemctl --user restart pipewire
```

### Problema: "PipeWire not running"

**Solução:**
```bash
systemctl --user start pipewire
systemctl --user start pipewire-pulse
```

### Problema: Som continua sem equalização

**Verificar:**
```bash
pw-cli ls  # Verificar se nó aparece
pw-cli dump 0 core  # Conferir se filter-chain está carregado
```

### Problema: Arquivo .conf com erro de sintaxe

**Verificar logs:**
```bash
journalctl --user -u pipewire -n 50 -f
```

### Problema: Arquivo corrompido

**Deletar e recrear:**
```bash
rm ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
# Reiniciar aplicação - vai recrear
```

---

## Performance e Otimizações

### Tempo de Reload
- Reload completo: ~100-200ms
- Perceptível ao usuário: sim, mas breve
- Aceito na prática: sim

### Threading Obrigatório
Sempre usar `threading.Thread` + `GLib.idle_add()` para:
- Não congelar interface
- Manter responsividade

### Cache de Presets
PresetManager deve manter cache em memória:
```python
def __init__(self):
    self.presets_cache = self.list_presets()
```

---

## Exemplo Completo: Fluxo de Ajuste

```
1. User move slider de 150Hz para +2.5dB
   
2. on_slider_changed(slider, band_index=1) chamado
   
3. self.gains[150] = 2.5
   
4. generate_pipewire_config({60: 0.0, 150: 2.5, 400: 0.0, ...})
   ├─ Cria string Lua com todos filtros
   └─ Escreve em ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
   
5. threading.Thread(reload_config()) inicia
   
6. reload_config() executa:
   systemctl --user restart pipewire
   
7. ~100-200ms de processamento
   
8. GLib.idle_add(update_status, "Ajuste em tempo real...")
   
9. UI atualiza status bar
   
10. User ouve mudança na música
```

---

**Fim do Guia de Integração**
