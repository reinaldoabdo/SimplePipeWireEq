# SimplePipeWireEQ - Especificação Completa do Projeto

## 1. VISÃO GERAL

**Nome:** SimplePipeWireEQ  
**Objetivo:** Interface GTK4 minimalista para equalizador de 10 canais para PipeWire no Linux  
**Tecnologia:** Python 3.10+ + GTK4 + libadwaita  
**Compatibilidade:** GNOME, KDE, XFCE e desktops compatíveis com GTK4

---

## 2. FUNCIONALIDADES PRINCIPAIS

### 2.1 Interface Visual
- **Layout:** Minimalista e intuitivo
- **10 Sliders:** Um para cada banda de frequência
- **Display de valores:** Mostrar ganho em dB ao lado de cada slider
- **Botão Play/Pause:** Para testar som enquanto ajusta (opcional)
- **Select de Presets:** Dropdown com presets salvos
- **Botões de Ação:** 
  - "Salvar Preset" (salva com nome customizado)
  - "Carregar Preset" (carrega preset selecionado)
  - "Resetar" (volta tudo para 0dB)
  - "Deletar Preset" (remove preset selecionado)
- **Status Bar:** Mostra último preset carregado/salvo e status da recarga

### 2.2 Bandas de Frequência (10 Canais)

| # | Frequência | Tipo | Uso |
|---|-----------|------|-----|
| 1 | 60 Hz | Bass | Graves profundos |
| 2 | 150 Hz | Bass | Baixo (kick drum) |
| 3 | 400 Hz | Low-Mid | Corpos de instrumentos |
| 4 | 1 kHz | Midrange | Presença (vozes) |
| 5 | 2.5 kHz | Midrange | Clareza |
| 6 | 4 kHz | Upper-Mid | Brilho |
| 7 | 8 kHz | Presence | Detalhe, sibilância |
| 8 | 12 kHz | Brilliance | Harmônicos altos |
| 9 | 16 kHz | Brilliance | Extensão aguda |
| 10 | 20 kHz | Brilliance | Limite superior audível |

**Características dos Sliders:**
- Range: -12dB a +12dB
- Step: 0.5dB
- Cor: Verde quando > 0dB, Azul quando < 0dB, Cinza quando = 0dB

---

## 3. ESTRUTURA DE ARQUIVOS

```
SimplePipeWireEQ/
├── README.md
├── requirements.txt
├── setup.py
├── .gitignore
├── src/
│   └── simplepipewireq/
│       ├── __init__.py
│       ├── main.py
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py
│       │   ├── eq_slider.py
│       │   └── preset_manager_ui.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config_manager.py
│       │   ├── pipewire_manager.py
│       │   └── preset_manager.py
│       └── utils/
│           ├── __init__.py
│           └── constants.py
├── data/
│   ├── com.github.simplepipewireq.desktop
│   └── icons/
│       └── simplepipewireq.svg
└── tests/
    ├── __init__.py
    ├── test_config_manager.py
    └── test_preset_manager.py
```

---

## 4. FLUXO DE DADOS

### 4.1 Primeira Inicialização

```
App inicia
    ↓
PipeWireManager.is_configured() → False
    ↓
PipeWireManager.setup_initial_config()
    ├─ gera ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
    ├─ com todos ganhos em 0dB
    └─ executa systemctl --user restart pipewire
    ↓
Dialog: "Configuração inicial concluída!"
    ↓
App inicia normal
```

### 4.2 Fluxo de Ajuste em Tempo Real

```
User Move Slider
    ↓
eq_slider.py emite sinal "value-changed"
    ↓
MainWindow.on_slider_changed() é chamado
    ↓
config_manager.write_config("temp.conf", gains_dict)
    ↓
pipewire_manager.generate_pipewire_config(gains_dict)
    ├─ atualiza ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
    └─ com novos valores
    ↓
threading.Thread(pipewire_manager.reload_config())
    ├─ executa: systemctl --user restart pipewire
    └─ user ouve mudança (~100-200ms depois)
    ↓
GLib.idle_add(update_status, "Ajuste em tempo real...")
```

### 4.3 Fluxo de Salvamento de Preset

```
User clica "Salvar Preset"
    ↓
Dialog pede nome: "Meu Pop Rock"
    ↓
preset_manager.validate_preset_name() → valida
    ↓
preset_manager.save_preset("MeuPopRock", gains_dict)
    ├─ cria ~/.config/pipewire/MeuPopRock.conf
    └─ com configuração atual
    ↓
preset_manager.list_presets() → recarrega cache
    ↓
MainWindow.refresh_preset_list()
    └─ "Meu Pop Rock" aparece no dropdown
    ↓
Status bar: "Preset 'Meu Pop Rock' salvo com sucesso"
```

### 4.4 Fluxo de Carregamento de Preset

```
User seleciona preset no dropdown
    ↓
MainWindow.on_load_preset("MeuPopRock")
    ↓
preset_manager.get_preset_gains("MeuPopRock")
    └─ lê ~/.config/pipewire/MeuPopRock.conf
    ↓
parse_preset_file() extrai gains
    └─ retorna {60: 0.5, 150: -1.0, ...}
    ↓
MainWindow atualiza visualmente 10 sliders
    ↓
config_manager.write_config("temp.conf", gains_dict)
    ↓
pipewire_manager.generate_pipewire_config(gains_dict)
    ↓
threading.Thread(pipewire_manager.reload_config())
    ↓
User ouve o preset carregado
```

---

## 5. ARQUIVOS DE CONFIGURAÇÃO

### 5.1 Arquivo Temporário (temp.conf)

**Localização:** `~/.config/pipewire/temp.conf`

**Formato:** INI simples

```ini
# SimplePipeWireEQ - Configuração Temporária
# Gerada automaticamente pela aplicação

[equalizer]
gain_60hz = 0.0
gain_150hz = 0.0
gain_400hz = 0.0
gain_1khz = 0.0
gain_2_5khz = 0.0
gain_4khz = 0.0
gain_8khz = 0.0
gain_12khz = 0.0
gain_16khz = 0.0
gain_20khz = 0.0
```

### 5.2 Arquivo de Configuração PipeWire

**Localização:** `~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf`

**Formato:** Lua (nativo do PipeWire)

Exemplo com ganhos reais:

```lua
# SimplePipeWireEQ - Configuração de Equalizador Paramétrico
# Gerada automaticamente pela aplicação

context.modules = [
    {
        name = libpipewire-module-filter-chain
        args = {
            node.description = "SimplePipeWireEQ Equalizer Sink"
            media.name = "SimplePipeWireEQ Equalizer Sink"
            filter.graph = {
                nodes = [
                    {
                        type = builtin
                        name = eq
                        label = param_eq
                        config = {
                            filters = [
                                { type = bq_peaking, freq = 60, gain = 0.0, q = 0.707 },
                                { type = bq_peaking, freq = 150, gain = 2.5, q = 0.707 },
                                { type = bq_peaking, freq = 400, gain = -1.0, q = 0.707 },
                                { type = bq_peaking, freq = 1000, gain = 0.0, q = 0.707 },
                                { type = bq_peaking, freq = 2500, gain = 1.5, q = 0.707 },
                                { type = bq_peaking, freq = 4000, gain = 0.0, q = 0.707 },
                                { type = bq_peaking, freq = 8000, gain = -0.5, q = 0.707 },
                                { type = bq_peaking, freq = 12000, gain = 3.0, q = 0.707 },
                                { type = bq_peaking, freq = 16000, gain = 0.0, q = 0.707 },
                                { type = bq_peaking, freq = 20000, gain = 1.0, q = 0.707 }
                            ]
                        }
                    }
                ]
                links = []
            }
            capture.props = {
                node.name = "effect_input.simplepipewireq"
                media.class = "Audio/Sink"
                audio.channels = 2
                audio.position = [ FL FR ]
            }
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

### 5.3 Arquivo de Preset Salvo

**Localização:** `~/.config/pipewire/<NomePreset>.conf`

**Formato:** Lua (idêntico ao 99-simplepipewireq.conf, apenas com valores salvos)

Exemplo: `~/.config/pipewire/MeuRock.conf`

---

## 6. MÓDULOS E RESPONSABILIDADES

### 6.1 main.py

Entry point da aplicação. Cria e executa a aplicação GTK.

```python
import sys
import logging
from gi.repository import Adw
from simplepipewireq.ui.main_window import MainWindow

logger = logging.getLogger(__name__)

class SimplePipeWireEQApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.github.simplepipewireq")
        
    def do_activate(self):
        """Ativado quando app é iniciado"""
        # Verificar e configurar PipeWire se necessário
        from simplepipewireq.core.pipewire_manager import PipeWireManager
        pw_manager = PipeWireManager()
        
        if not pw_manager.is_configured():
            logger.info("Configuração inicial não encontrada, criando...")
            if not pw_manager.setup_initial_config():
                logger.error("Falha ao configurar PipeWire")
                # Dialog de erro
        
        window = MainWindow(self)
        window.present()

def main():
    """Entry point da aplicação"""
    app = SimplePipeWireEQApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()
```

### 6.2 constants.py

Armazena todas as constantes da aplicação.

```python
import os
from pathlib import Path

# Frequências dos 10 canais
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
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 600
APP_NAME = "SimplePipeWireEQ"
APP_VERSION = "1.0.0"
```

### 6.3 config_manager.py

Gerencia leitura/escrita de arquivos .conf (INI) com ganhos.

**Responsabilidades:**
- Ler/escrever temp.conf
- Validar valores de ganho
- Criar diretório ~/.config/pipewire/ se não existir

**Métodos principais:**
```python
class ConfigManager:
    def read_config(self, filename: str) -> dict:
        """Lê arquivo .conf e retorna dict de ganhos"""
        # Retorna: {60: 0.0, 150: 0.5, ...}
    
    def write_config(self, filename: str, gains_dict: dict) -> bool:
        """Escreve dict de ganhos em arquivo .conf"""
    
    def validate_gain(self, value: float) -> bool:
        """Valida se gain está entre -12 e +12"""
    
    def get_temp_config_path(self) -> Path:
        """Retorna ~/.config/pipewire/temp.conf"""
```

### 6.4 pipewire_manager.py

Gerencia integração com PipeWire.

**Responsabilidades:**
- Gerar arquivo Lua válido para PipeWire
- Executar reload do PipeWire
- Verificar se PipeWire está rodando
- Setup inicial na primeira execução

**Métodos principais:**
```python
class PipeWireManager:
    def is_configured(self) -> bool:
        """Verifica se 99-simplepipewireq.conf existe"""
    
    def setup_initial_config(self) -> bool:
        """Cria configuração inicial (todos ganhos em 0dB)"""
    
    def generate_pipewire_config(self, gains_dict: dict) -> bool:
        """Gera arquivo Lua válido para PipeWire"""
    
    def reload_config(self) -> bool:
        """Executa: systemctl --user restart pipewire"""
    
    def is_pipewire_running(self) -> bool:
        """Verifica se PipeWire está ativo"""
    
    def parse_preset_file(self, filepath: Path) -> dict:
        """Parse arquivo Lua para extrair ganhos"""
```

### 6.5 preset_manager.py

Gerencia presets salvos.

**Responsabilidades:**
- Listar presets disponíveis
- Validar nomes de presets
- Salvar/deletar presets
- Cache em memória

**Métodos principais:**
```python
class PresetManager:
    def list_presets(self) -> list:
        """Retorna lista de nomes de presets"""
    
    def validate_preset_name(self, name: str) -> bool:
        """Valida nome (sem caracteres inválidos)"""
    
    def save_preset(self, name: str, gains_dict: dict) -> bool:
        """Salva novo preset"""
    
    def delete_preset(self, name: str) -> bool:
        """Deleta preset"""
    
    def get_preset_gains(self, name: str) -> dict:
        """Retorna dict de ganhos de um preset"""
```

### 6.6 main_window.py

Janela principal da aplicação.

**Responsabilidades:**
- Construir interface GTK
- Conectar sinais
- Gerenciar estado visual
- Coordenar lógica central

**Métodos principais:**
```python
class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        """Inicializa janela"""
    
    def setup_ui(self):
        """Cria layout com 10 sliders"""
    
    def on_slider_changed(self, slider, band_index):
        """Callback quando slider é movido"""
        # Escreve config
        # Gera arquivo PipeWire
        # Recarrega em thread
    
    def on_load_preset(self, preset_name):
        """Carrega preset"""
    
    def on_save_preset(self):
        """Abre dialog para salvar"""
    
    def on_reset(self):
        """Reseta todos sliders"""
    
    def on_delete_preset(self, preset_name):
        """Deleta preset"""
    
    def refresh_preset_list(self):
        """Recarrega dropdown de presets"""
    
    def update_status(self, message: str):
        """Atualiza status bar"""
```

### 6.7 eq_slider.py

Widget customizado GTK4 para slider EQ.

**Responsabilidades:**
- Renderizar slider vertical/horizontal
- Exibir valor em dB
- Colorir conforme ganho
- Emitir sinais

**Métodos principais:**
```python
class EQSlider(Gtk.Box):
    def __init__(self, frequency: int, min_val=-12, max_val=12):
        """Cria slider com label e valor"""
    
    def get_value(self) -> float:
        """Retorna valor em dB"""
    
    def set_value(self, value: float):
        """Define valor em dB"""
    
    def connect_value_changed(self, callback):
        """Conecta callback para mudanças"""
```

---

## 7. LAYOUT UI/UX

```
┌─────────────────────────────────────────────┐
│ SimplePipeWireEQ                        [‾] │
├─────────────────────────────────────────────┤
│                                             │
│ Preset: [▼ Meu Rock ──────────────────────] │
│ [Load] [Save] [Delete] [Reset]             │
│                                             │
│ ┌──────────────────────────────────────────┐│
│ │ 60Hz   150Hz  400Hz  1kHz   2.5kHz      ││
│ │   │      │      │      │       │        ││
│ │  ▲▲    ▲▲    ▼▼    ──    ▲▲   ││
│ │  0dB   +2dB  -1dB   0dB  +1dB ││
│ │                              ││
│ │ 4kHz   8kHz  12kHz  16kHz  20kHz       ││
│ │   │      │      │       │      │       ││
│ │  ──    ▼▼    ▲▲    ──    ▲▲   ││
│ │  0dB   -2dB  +3dB  0dB   +1dB ││
│ └──────────────────────────────────────────┘│
│                                             │
│ ✓ Último preset: "Meu Rock" carregado      │
└─────────────────────────────────────────────┘
```

---

## 8. REQUISITOS TÉCNICOS

### Dependências Python
```
gtk4>=4.10.0
PyGObject>=3.46.0
libadwaita>=1.3.0
```

### Dependências do Sistema
```
libgtk-4-1
libadwaita-1
gobject-introspection
systemd (para systemctl)
pipewire (>= 0.3.0)
pipewire-audio ou pipewire-alsa + pipewire-pulse
```

### Python Version
```
Python >= 3.10
```

---

## 9. FLUXO DE EXECUÇÃO (User Journey)

### Cenário 1: Primeira Execução

1. User instala e executa SimplePipeWireEQ
2. App verifica se `99-simplepipewireq.conf` existe
3. Se não existe, cria com ganhos em 0dB
4. Executa `systemctl --user restart pipewire`
5. Dialog: "Configuração inicial concluída!"
6. App inicia normal

### Cenário 2: Ajuste em Tempo Real

1. App está rodando com música tocando
2. User move slider de 60Hz para +3dB
3. `on_slider_changed()` é chamado
4. ConfigManager escreve temp.conf
5. PipeWireManager gera arquivo Lua atualizado
6. Thread recarrega PipeWire
7. ~100-200ms depois, user ouve mudança
8. Status bar mostra "Ajuste em tempo real"

### Cenário 3: Salvar Preset Personalizado

1. User ajusta vários sliders
2. Clica "Salvar Preset"
3. Dialog: "Nome do preset?" → "Meu Rock"
4. PresetManager valida nome
5. Cria `~/.config/pipewire/MeuRock.conf`
6. Recarrega dropdown
7. "Meu Rock" aparece na lista
8. Status bar: "Preset 'Meu Rock' salvo"

### Cenário 4: Carregar Preset

1. User abre dropdown de presets
2. Seleciona "Meu Rock"
3. `on_load_preset()` é chamado
4. PresetManager lê arquivo do preset
5. MainWindow atualiza visualmente 10 sliders
6. PipeWireManager gera arquivo com valores
7. Thread recarrega PipeWire
8. User ouve o preset carregado

---

## 10. TRATAMENTO DE ERROS

| Cenário | Ação |
|---------|------|
| PipeWire não está rodando | Dialog: "PipeWire não está ativo. Inicie com: systemctl --user start pipewire" |
| Falha ao gerar config | Dialog: "Erro ao gerar configuração. Tente novamente." |
| Falha ao recarregar | Dialog: "Erro ao recarregar PipeWire. Verifique logs com: journalctl --user -u pipewire" |
| Nome de preset inválido | Dialog: "Nome contém caracteres inválidos. Use apenas letras, números, espaços e hífen." |
| Preset não encontrado | Remover da lista, avisar user |
| Arquivo .conf corrompido | Resetar para defaults, log do erro |
| Arquivo .conf com permissões erradas | Dialog: "Sem permissão para escrever em ~/.config/pipewire" |

---

## 11. TESTES UNITÁRIOS

### test_config_manager.py
```python
def test_read_valid_config()
def test_write_config()
def test_validate_gain_valid()
def test_validate_gain_invalid()
def test_create_config_dir_if_not_exists()
def test_get_temp_config_path()
```

### test_preset_manager.py
```python
def test_list_presets()
def test_save_preset()
def test_delete_preset()
def test_validate_preset_name_valid()
def test_validate_preset_name_invalid()
def test_get_preset_gains()
```

---

## 12. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Setup.py e estrutura de projeto
- [ ] requirements.txt com dependências
- [ ] .gitignore configurado
- [ ] constants.py com todas constantes
- [ ] ConfigManager leitura/escrita de .conf
- [ ] PipeWireManager geração de Lua
- [ ] PipeWireManager reload funcional
- [ ] PipeWireManager setup inicial
- [ ] PresetManager listagem e gerenciamento
- [ ] EQSlider widget customizado
- [ ] MainWindow layout base
- [ ] 10 sliders conectados
- [ ] Dropdown de presets
- [ ] Botões (Load, Save, Delete, Reset)
- [ ] Threading para reload
- [ ] GLib.idle_add para UI updates
- [ ] Callbacks conectados
- [ ] Status bar atualizado
- [ ] Dialogs de validação
- [ ] Tratamento de erros
- [ ] Testes unitários
- [ ] Desktop entry (.desktop file)
- [ ] README com instruções
- [ ] Testes de UX real

---

## 13. NOTAS ADICIONAIS

- **Performance:** Reload deve ser rápido (<500ms total)
- **UI Responsiva:** Nunca travar durante reload (sempre threading)
- **Acessibilidade:** Labels descritivos, keyboard navigation
- **Logging:** Tudo logado para debugging
- **Thread-Safety:** Usar GLib.idle_add() para UI updates de threads

---

**Fim da Especificação**