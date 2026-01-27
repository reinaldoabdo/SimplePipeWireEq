# SimplePipeWireEQ - Especificação Detalhada do Projeto

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
- **Botão Play/Pause:** Para testar som enquanto ajusta (opcional, requer player padrão)
- **Select de Presets:** Dropdown com presets salvos
- **Botões de Ação:** 
  - "Salvar Preset" (salva com nome customizado)
  - "Carregar Preset" (carrega preset selecionado)
  - "Resetar" (volta tudo para 0dB)
  - "Deletar Preset" (remove preset selecionado)
- **Status Bar:** Mostra último preset carregado/salvo e status da recarga

### 2.2 Bandas de Frequência (10 Canais)
As 10 bandas devem cobrir o espectro de frequência comum em players MP3:

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
- Formato visual: Vertical ou Horizontal (design choice)
- Cor: Virar verde quando > 0dB, vermelho quando < 0dB (opcional)

---

## 3. ESTRUTURA DE ARQUIVOS

```
SimplePipeWireEQ/
├── README.md
├── requirements.txt
├── setup.py
├── src/
│   └── simplepipewireq/
│       ├── __init__.py
│       ├── main.py                 # Entry point
│       ├── ui/
│       │   ├── __init__.py
│       │   ├── main_window.py      # Classe da janela principal
│       │   ├── eq_slider.py        # Widget customizado para slider EQ
│       │   └── preset_manager_ui.py # Diálogos de preset
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config_manager.py   # Gerenciamento de arquivos .conf
│       │   ├── pipewire_manager.py # Comunicação com PipeWire
│       │   └── preset_manager.py   # Lógica de presets
│       └── utils/
│           ├── __init__.py
│           └── constants.py         # Constantes (frequências, paths, etc)
├── data/
│   ├── com.github.simplepipewireq.desktop  # Desktop entry
│   └── icons/
│       └── simplepipewireq.svg
└── tests/
    ├── __init__.py
    ├── test_config_manager.py
    └── test_preset_manager.py
```

---

## 4. FLUXO DE DADOS

### 4.1 Fluxo de Ajuste em Tempo Real

```
User Moves Slider
    ↓
eq_slider.py (widget) emite sinal "value-changed"
    ↓
main_window.py captura sinal
    ↓
config_manager.py escreve valores em ~/.config/pipewire/temp.conf
    ↓
pipewire_manager.py chama systemctl --user restart pipewire
    ↓
PipeWire recarrega filtros com novos valores
    ↓
User ouve mudança (com breve clique de ~100-200ms)
    ↓
Status bar atualiza com timestamp
```

### 4.2 Fluxo de Salvamento de Preset

```
User clica "Salvar Preset"
    ↓
Dialog pede nome do preset (ex: "Meu Pop Rock")
    ↓
preset_manager.py valida nome (sem caracteres inválidos)
    ↓
config_manager.py copia temp.conf → ~/.config/pipewire/MeuPopRock.conf
    ↓
preset_manager.py atualiza lista de presets em memória
    ↓
main_window.py recarrega dropdown de presets
    ↓
Status bar mostra "Preset 'Meu Pop Rock' salvo com sucesso"
```

### 4.3 Fluxo de Carregamento de Preset

```
User seleciona preset no dropdown
    ↓
main_window.py captura seleção
    ↓
config_manager.py lê arquivo ~/.config/pipewire/PresetName.conf
    ↓
Extrai valores de ganho para cada frequência
    ↓
main_window.py atualiza todos os 10 sliders visualmente
    ↓
config_manager.py copia preset → temp.conf
    ↓
pipewire_manager.py dispara reload
    ↓
User ouve o preset carregado
```

---

## 5. ARQUIVOS DE CONFIGURAÇÃO

### 5.1 Estrutura do temp.conf (e presets salvos)

```ini
# SimplePipeWireEQ - Configuração Temporária
# Gerada automaticamente pela aplicação

[equalizer]
# Banda 1: 60 Hz
gain_60hz = 0.0

# Banda 2: 150 Hz
gain_150hz = 0.0

# Banda 3: 400 Hz
gain_400hz = 0.0

# Banda 4: 1 kHz
gain_1khz = 0.0

# Banda 5: 2.5 kHz
gain_2_5khz = 0.0

# Banda 6: 4 kHz
gain_4khz = 0.0

# Banda 7: 8 kHz
gain_8khz = 0.0

# Banda 8: 12 kHz
gain_12khz = 0.0

# Banda 9: 16 kHz
gain_16khz = 0.0

# Banda 10: 20 kHz
gain_20khz = 0.0
```

**Localização:**
- Temporário: `~/.config/pipewire/temp.conf`
- Presets salvos: `~/.config/pipewire/<NomePreset>.conf`

### 5.2 Integração com PipeWire

O arquivo .conf será utilizado pelo PipeWire para carregar os filtros.  
A aplicação **não modifica** a configuração principal do PipeWire, apenas gerencia seus próprios arquivos.

---

## 6. MÓDULOS E RESPONSABILIDADES

### 6.1 `main.py`
- Inicializa aplicação GTK
- Cria janela principal
- Gerencia ciclo de vida da aplicação
- Função `main()` é o entry point

```python
def main():
    """Entry point da aplicação"""
    app = SimplePipeWireEQApp()
    return app.run(sys.argv)
```

### 6.2 `main_window.py` - Classe `MainWindow`
**Responsabilidades:**
- Construir interface GTK (layout, widgets)
- Gerenciar estado visual (sliders, labels, dropdown)
- Conectar sinais de widgets a métodos
- Atualizar UI quando presets carregam
- Coordenar chamadas para ConfigManager e PresetManager

**Métodos principais:**
```python
class MainWindow:
    def __init__(self):
        """Inicializa janela e widgets"""
    
    def setup_ui(self):
        """Cria layout GTK com 10 sliders"""
    
    def on_slider_changed(self, slider, band_index):
        """Callback quando slider é movido"""
        # Atualiza temp.conf
        # Recarrega PipeWire
        # Atualiza display de valor
    
    def on_load_preset(self, preset_name):
        """Carrega preset selecionado"""
        # Lê arquivo do preset
        # Atualiza sliders visualmente
        # Escreve em temp.conf
        # Recarrega PipeWire
    
    def on_save_preset(self, preset_name):
        """Abre dialog para salvar preset com nome"""
    
    def on_reset(self):
        """Reseta todos sliders para 0dB"""
    
    def on_delete_preset(self, preset_name):
        """Deleta preset do filesystem"""
    
    def refresh_preset_list(self):
        """Recarrega dropdown de presets"""
    
    def update_status(self, message):
        """Atualiza status bar"""
```

### 6.3 `config_manager.py` - Classe `ConfigManager`
**Responsabilidades:**
- Ler/escrever arquivos .conf (temp.conf e presets)
- Validar valores de ganho (-12dB a +12dB)
- Garantir existência de diretório `~/.config/pipewire/`
- Parse de valores para float

**Métodos principais:**
```python
class ConfigManager:
    def __init__(self):
        """Inicializa, cria diretório se não existir"""
    
    def read_config(self, filename):
        """Lê arquivo .conf e retorna dict com ganhos"""
        # Retorna: {60: 0.0, 150: 0.5, ...}
    
    def write_config(self, filename, gains_dict):
        """Escreve dict de ganhos em arquivo .conf"""
        # gains_dict = {60: 0.0, 150: 0.5, ...}
    
    def validate_gain(self, value):
        """Valida se gain está entre -12 e +12"""
    
    def get_temp_config_path(self):
        """Retorna ~/.config/pipewire/temp.conf"""
    
    def get_preset_path(self, preset_name):
        """Retorna ~/.config/pipewire/<PresetName>.conf"""
```

### 6.4 `pipewire_manager.py` - Classe `PipeWireManager`
**Responsabilidades:**
- Executar comando de reload do PipeWire
- Verificar se PipeWire está rodando
- Capturar erros de comunicação
- Log de operações

**Métodos principais:**
```python
class PipeWireManager:
    def reload_config(self):
        """Executa: systemctl --user restart pipewire"""
        # Captura stderr/stdout
        # Retorna True se sucesso, False se falha
    
    def is_pipewire_running(self):
        """Verifica se PipeWire está ativo"""
        # Executa: systemctl --user is-active pipewire
    
    def handle_reload_error(self, error):
        """Trata erros de reload gracefully"""
```

### 6.5 `preset_manager.py` - Classe `PresetManager`
**Responsabilidades:**
- Listar presets disponíveis
- Validar nomes de presets
- Copiar/deletar arquivos de preset
- Gerenciar metadata (lista em cache)

**Métodos principais:**
```python
class PresetManager:
    def __init__(self):
        """Inicializa e carrega lista de presets"""
    
    def list_presets(self):
        """Retorna lista de nomes de presets disponíveis"""
        # Varre ~/.config/pipewire/*.conf (exceto temp.conf)
    
    def validate_preset_name(self, name):
        """Valida nome (sem /, \, etc)"""
    
    def save_preset(self, name, gains_dict):
        """Salva novo preset"""
        # Escreve arquivo
        # Atualiza cache
    
    def delete_preset(self, name):
        """Deleta arquivo de preset"""
    
    def get_preset_gains(self, name):
        """Retorna dict de ganhos de um preset"""
```

### 6.6 `eq_slider.py` - Classe `EQSlider`
**Responsabilidades:**
- Widget customizado GTK4 para slider EQ
- Emitir sinais quando valor muda
- Exibir valor em dB
- Colorir conforme valor (verde/red)

**Métodos principais:**
```python
class EQSlider(Gtk.Box):
    def __init__(self, frequency, min_val=-12, max_val=12):
        """Cria slider com label de frequência e valor"""
    
    def get_value(self):
        """Retorna valor atual em dB"""
    
    def set_value(self, value):
        """Define valor em dB"""
    
    def connect_value_changed(self, callback):
        """Conecta callback para mudanças"""
```

### 6.7 `constants.py`
**Armazena:**
```python
# Frequências dos 10 canais
FREQUENCIES = [60, 150, 400, 1000, 2500, 4000, 8000, 12000, 16000, 20000]

# Range de ganho
MIN_GAIN = -12.0
MAX_GAIN = 12.0
GAIN_STEP = 0.5

# Paths
CONFIG_DIR = os.path.expanduser("~/.config/pipewire")
TEMP_CONF = os.path.join(CONFIG_DIR, "temp.conf")

# Comandos
PIPEWIRE_RELOAD_CMD = ["systemctl", "--user", "restart", "pipewire"]
PIPEWIRE_STATUS_CMD = ["systemctl", "--user", "is-active", "pipewire"]

# UI
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
APP_NAME = "SimplePipeWireEQ"
```

---

## 7. FLUXO DE EXECUÇÃO (User Journey)

### Cenário 1: Usuário ajusta equalizador em tempo real

1. App inicia, carrega último preset (ou defaults)
2. Usuário move slider de 60Hz para +3dB
3. `on_slider_changed()` é chamado
4. ConfigManager escreve temp.conf com novo valor
5. PipeWireManager executa `systemctl --user restart pipewire`
6. PipeWire recarrega com novo filtro
7. User ouve mudança (~100ms depois)
8. Status bar mostra "Ajuste em tempo real"

### Cenário 2: Usuário salva preset personalizado

1. User ajusta vários sliders
2. Clica "Salvar Preset"
3. Dialog pede nome: "Meu Rock"
4. PresetManager valida nome
5. ConfigManager copia temp.conf → MeuRock.conf
6. UI recarrega dropdown de presets
7. "Meu Rock" aparece na lista
8. Status bar: "Preset 'Meu Rock' salvo"

### Cenário 3: Usuário carrega preset existente

1. User clica dropdown de presets
2. Seleciona "Meu Rock"
3. `on_load_preset()` é chamado
4. ConfigManager lê MeuRock.conf
5. MainWindow atualiza visualmente todos 10 sliders
6. ConfigManager escreve valores em temp.conf
7. PipeWireManager recarrega PipeWire
8. User ouve o preset

---

## 8. REQUISITOS TÉCNICOS

### 8.1 Dependências Python
```
gtk4>=4.10.0
PyGObject>=3.46.0
libadwaita>=1.3.0
```

### 8.2 Dependências do Sistema
```
libgtk-4-1
libadwaita-1
gobject-introspection
systemd (para systemctl)
pipewire (óbvio)
```

### 8.3 Python Version
```
Python >= 3.10
```

---

## 9. TRATAMENTO DE ERROS

| Cenário | Ação |
|---------|------|
| PipeWire não está rodando | Dialog: "PipeWire não está ativo. Inicie-o primeiro." |
| Falha ao recarregar | Dialog: "Erro ao recarregar PipeWire. Tente novamente." |
| Arquivo .conf corrompido | Resetar para defaults, log do erro |
| Nome de preset inválido | Dialog: "Nome contém caracteres inválidos" |
| Preset não encontrado | Remover da lista, avisar usuário |

---

## 10. DESIGN UI/UX

### 10.1 Layout Proposto
```
┌─────────────────────────────────────────┐
│ SimplePipeWireEQ                    [‾] │
├─────────────────────────────────────────┤
│                                         │
│  Preset: [▼ Meu Rock ──────────────]   │
│  [Load] [Save] [Delete] [Reset]        │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ 60Hz   │ 150Hz  │ 400Hz  │ 1kHz   │ │
│  │   ▲    │   ▲    │   ▲    │   ▲    │ │
│  │  ─0dB  │  +2dB  │  -1dB  │  +3dB  │ │
│  │   │    │   │    │   │    │   │    │ │
│  │   ▼    │   ▼    │   ▼    │   ▼    │ │
│  │        │        │        │        │ │
│  │ 2.5kHz │ 4kHz   │ 8kHz   │ 12kHz  │ │
│  │   ▲    │   ▲    │   ▲    │   ▲    │ │
│  │  +1dB  │  -2dB  │   0dB  │  +4dB  │ │
│  │   │    │   │    │   │    │   │    │ │
│  │   ▼    │   ▼    │   ▼    │   ▼    │ │
│  │        │        │        │        │ │
│  │ 16kHz  │ 20kHz  │        │        │ │
│  │   ▲    │   ▲    │        │        │ │
│  │   0dB  │  +2dB  │        │        │ │
│  │   │    │   │    │        │        │ │
│  │   ▼    │   ▼    │        │        │ │
│  └───────────────────────────────────┘ │
│                                         │
│ ✓ Último preset: "Meu Rock" carregado  │
└─────────────────────────────────────────┘
```

### 10.2 Paleta de Cores
- Fundo: Cinza neutro (tema do sistema)
- Sliders em 0dB: Cinza
- Sliders em +dB: Verde
- Sliders em -dB: Azul ou Laranja
- Botões: Primário (azul)

### 10.3 Iconografia
- Play icon para teste (opcional)
- Ícone de salvamento
- Ícone de delete (lixeira)
- Ícone de reset (seta circular)

---

## 11. TESTES UNITÁRIOS

### 11.1 test_config_manager.py
```python
def test_read_valid_config()
def test_write_config()
def test_validate_gain_valid()
def test_validate_gain_invalid()
def test_create_config_dir_if_not_exists()
```

### 11.2 test_preset_manager.py
```python
def test_list_presets()
def test_save_preset()
def test_delete_preset()
def test_validate_preset_name_valid()
def test_validate_preset_name_invalid()
```

---

## 12. CHECKLIST DE IMPLEMENTAÇÃO

- [ ] Setup.py e estrutura de projeto
- [ ] requirements.txt com dependências
- [ ] constants.py com todas as constantes
- [ ] ConfigManager leitura/escrita de .conf
- [ ] PipeWireManager reload funcional
- [ ] PresetManager listagem e gerenciamento
- [ ] EQSlider widget customizado
- [ ] MainWindow layout base
- [ ] 10 sliders conectados
- [ ] Dropdown de presets
- [ ] Botões (Load, Save, Delete, Reset)
- [ ] Callbacks conectados
- [ ] Status bar atualizado
- [ ] Dialogs de validação
- [ ] Tratamento de erros
- [ ] Testes unitários
- [ ] Desktop entry (.desktop file)
- [ ] README com instruções de instalação
- [ ] Testes de UX real

---

## 13. NOTAS ADICIONAIS

### 13.1 Performance
- Reload deve ser rápido (<500ms)
- UI não deve travar durante reload
- Cache de presets em memória para evitar I/O constante

### 13.2 Acessibilidade
- Labels descritivos para todos widgets
- Keyboard navigation funcional
- Alto contraste para sliders

### 13.3 Localização (i18n)
- Preparar estrutura para tradução (não necessário inicialmente)
- Usar gettext se implementar depois

### 13.4 Integração Futura
- Possibilidade de adicionar mais bandas de frequência
- Possibilidade de pré-presets built-in (Pop, Rock, Jazz, etc)
- Análise visual (spectrum analyzer)
- Gravação de áudio para benchmark

---

## 14. DOCUMENTAÇÃO NECESSÁRIA

- README.md: Instruções de uso, instalação, requerimentos
- CONTRIBUTING.md: Como contribuir (opcional)
- Manual.md: Guia de uso da interface
- API.md: Documentação das classes e métodos (opcional)

---

**Fim da Especificação**
