# SimplePipeWireEQ - Rastreamento de Progresso

**Última atualização:** [DATA/HORA]  
**Status Geral:** Não iniciado

---

## Estrutura de Status

```
[ ] = Não iniciado
[🔄] = Em andamento
[✅] = Completo e testado
[❌] = Falhou - Ação necessária
```

---

## Fase 1: Setup Inicial

- [✅] **Setup.1** - Criar estrutura de diretórios
  ```
  src/simplepipewireq/{__init__.py, core/, ui/, utils/}
  tests/{__init__.py}
  data/
  ```
  - **Responsável:** Agente
  - **Comando:** `mkdir -p src/simplepipewireq/{core,ui,utils} tests data`
  - **Estimativa:** 2 minutos
  - **Notas:** 

- [✅] **Setup.2** - Criar arquivos vazios com docstrings
  - `__init__.py` em cada pasta
  - `src/simplepipewireq/__init__.py` com versão
  - **Responsável:** Agente
  - **Estimativa:** 5 minutos
  - **Verificação:** `find . -name "*.py" | wc -l` deve = 10+

- [✅] **Setup.3** - Criar arquivos raiz
  - `requirements.txt`
  - `setup.py`
  - `.gitignore`
  - `README.md` (básico)
  - **Responsável:** Agente
  - **Estimativa:** 10 minutos
  - **Verificação:** Todos 4 arquivos existem na raiz

- [ ] **Setup.4** - Inicializar Git (opcional mas recomendado)
  ```bash
  git init
  git config user.name "Agent"
  git config user.email "agent@simplepipewireq"
  git add .
  git commit -m "Initial project structure"
  ```
  - **Responsável:** Agente
  - **Estimativa:** 2 minutos
  - **Verificação:** `git log` mostra commit inicial

---

## Fase 2: Módulos Core (Ordem Importante!)

### 2.1 - constants.py

- [ ] **Core.1.1** - Implementar `constants.py`
  - Frequências: `[60, 150, 400, 1000, 2500, 4000, 8000, 12000, 16000, 20000]`
  - Paths: `CONFIG_DIR`, `PIPEWIRE_CONFIG_FILE`, etc
  - Comandos: `PIPEWIRE_RELOAD_CMD`, etc
  - **Arquivo:** `src/simplepipewireq/utils/constants.py`
  - **Status:** [✅]
  - **Teste Manual:**
    ```python
    from simplepipewireq.utils.constants import FREQUENCIES
    assert len(FREQUENCIES) == 10
    assert FREQUENCIES[0] == 60
    ```
  - **Commit Message:** "feat: add constants module with frequencies and paths"
  - **Estimativa:** 5 minutos

---

### 2.2 - config_manager.py

- [ ] **Core.2.1** - Implementar `ConfigManager.__init__()`
  - Criar diretório `~/.config/pipewire/` se não existir
  - **Arquivo:** `src/simplepipewireq/core/config_manager.py`
  - **Status:** [✅]
  - **Teste:**
    ```python
    from simplepipewireq.core.config_manager import ConfigManager
    cm = ConfigManager()
    assert cm.get_temp_config_path().parent.exists()
    ```
  - **Estimativa:** 5 minutos

- [ ] **Core.2.2** - Implementar `ConfigManager.write_config()`
  - Escrever dict em arquivo INI
  - Formato: `[equalizer]\ngain_60hz = 0.0\n...`
  - **Status:** [✅]
  - **Teste:**
    ```python
    gains = {60: 0.0, 150: 1.5, ...}
    cm.write_config("test.conf", gains)
    # Ler arquivo e verificar conteúdo
    ```
  - **Estimativa:** 10 minutos

- [ ] **Core.2.3** - Implementar `ConfigManager.read_config()`
  - Ler arquivo INI e retornar dict
  - **Status:** [✅]
  - **Teste:**
    ```python
    gains = cm.read_config("test.conf")
    assert gains[60] == 0.0
    assert gains[150] == 1.5
    ```
  - **Estimativa:** 10 minutos

- [ ] **Core.2.4** - Implementar `ConfigManager.validate_gain()`
  - Validar se -12.0 <= gain <= 12.0
  - **Status:** [✅]
  - **Teste:**
    ```python
    assert cm.validate_gain(0.0) == True
    assert cm.validate_gain(12.0) == True
    assert cm.validate_gain(13.0) == False
    ```
  - **Estimativa:** 5 minutos

- [ ] **Core.2.5** - Teste Unitário: test_config_manager.py
  - Executar `pytest tests/test_config_manager.py`
  - Deve passar 100%
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [ ] **Commit** - "feat: implement ConfigManager for INI file handling"

---

### 2.3 - pipewire_manager.py

- [✅] **Core.3.1** - Implementar `PipeWireManager.__init__()`
  - Apenas inicializar logging
  - **Status:** [✅]
  - **Estimativa:** 2 minutos

- [✅] **Core.3.2** - Implementar `PipeWireManager.is_configured()`
  - Verificar se `99-simplepipewireq.conf` existe
  - **Status:** [✅]
  - **Teste:**
    ```python
    from simplepipewireq.core.pipewire_manager import PipeWireManager
    pm = PipeWireManager()
    # Deve retornar False se não existe
    assert isinstance(pm.is_configured(), bool)
    ```
  - **Estimativa:** 5 minutos

- [✅] **Core.3.3** - Implementar `PipeWireManager.generate_pipewire_config()`
  - Gerar arquivo Lua válido
  - Seguir template exatamente do INTEGRATION_GUIDE
  - **Status:** [✅]
  - **Teste Manual:**
    ```bash
    cat ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
    # Deve conter: context.modules = [ { name = libpipewire-module-filter-chain
    # Deve conter 10 filtros bq_peaking
    ```
  - **Estimativa:** 15 minutos

- [✅] **Core.3.4** - Implementar `PipeWireManager.reload_config()`
  - Executar `systemctl --user restart pipewire` com timeout=5
  - **Status:** [✅]
  - **Teste Manual:**
    ```bash
    systemctl --user is-active pipewire
    # Deve estar ativo antes/depois do reload
    ```
  - **⚠️ CUIDADO:** Isso INTERROMPE ÁUDIO. Testar com música ligada para verificar.
  - **Estimativa:** 10 minutos

- [✅] **Core.3.5** - Implementar `PipeWireManager.parse_preset_file()`
  - Fazer regex para extrair freq e gain de arquivo Lua
  - **Status:** [✅]
  - **Teste:**
    ```python
    # Criar arquivo Lua com filtros
    gains = pm.parse_preset_file(arquivo)
    assert gains[60] == 0.0
    assert gains[150] == 2.5
    ```
  - **Estimativa:** 15 minutos

- [✅] **Core.3.6** - Implementar `PipeWireManager.setup_initial_config()`
  - Chamar `generate_pipewire_config()` com todos 0dB
  - Chamar `reload_config()`
  - Retornar bool de sucesso
  - **Status:** [✅]
  - **Teste:**
    ```python
    success = pm.setup_initial_config()
    assert success == True
    assert pm.is_configured() == True
    ```
  - **Estimativa:** 5 minutos

- [ ] **Commit** - "feat: implement PipeWireManager for Lua generation and reloading"

---

### 2.4 - preset_manager.py

- [✅] **Core.4.1** - Implementar `PresetManager.__init__()`
  - Carregar lista de presets em cache
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [✅] **Core.4.2** - Implementar `PresetManager.list_presets()`
  - Varrer `~/.config/pipewire/*.conf` (exceto `temp.conf` e `99-simplepipewireq.conf`)
  - Retornar lista de nomes sem extensão
  - **Status:** [✅]
  - **Teste:**
    ```python
    from simplepipewireq.core.preset_manager import PresetManager
    pm = PresetManager()
    presets = pm.list_presets()
    assert isinstance(presets, list)
    ```
  - **Estimativa:** 10 minutos

- [✅] **Core.4.3** - Implementar `PresetManager.validate_preset_name()`
  - Regex: `r'[^\w\s-]'` para caracteres inválidos
  - Retornar bool
  - **Status:** [✅]
  - **Teste:**
    ```python
    assert pm.validate_preset_name("Meu Rock") == True
    assert pm.validate_preset_name("Rock/Pop") == False
    assert pm.validate_preset_name("Rock & Pop") == False
    ```
  - **Estimativa:** 5 minutos

- [✅] **Core.4.4** - Implementar `PresetManager.save_preset()`
  - Validar nome
  - Gerar arquivo `.conf` em `~/.config/pipewire/`
  - Atualizar cache
  - **Status:** [✅]
  - **Teste:**
    ```python
    gains = {60: 1.0, 150: 0.5, ...}
    success = pm.save_preset("TestBass", gains)
    assert success == True
    assert "TestBass" in pm.list_presets()
    ```
  - **Estimativa:** 10 minutos

- [✅] **Core.4.5** - Implementar `PresetManager.delete_preset()`
  - Deletar arquivo de preset
  - Atualizar cache
  - Retornar bool
  - **Status:** [✅]
  - **Teste:**
    ```python
    pm.save_preset("ToDelete", gains)
    assert "ToDelete" in pm.list_presets()
    success = pm.delete_preset("ToDelete")
    assert success == True
    assert "ToDelete" not in pm.list_presets()
    ```
  - **Estimativa:** 10 minutos

- [✅] **Core.4.6** - Implementar `PresetManager.get_preset_gains()`
  - Ler arquivo de preset
  - Chamar `PipeWireManager.parse_preset_file()`
  - Retornar dict de ganhos
  - **Status:** [✅]
  - **Teste:**
    ```python
    gains = pm.get_preset_gains("TestBass")
    assert isinstance(gains, dict)
    assert all(isinstance(v, float) for v in gains.values())
    ```
  - **Estimativa:** 5 minutos

- [✅] **Core.4.7** - Teste Unitário: test_preset_manager.py
  - Executar `pytest tests/test_preset_manager.py`
  - Deve passar 100%
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [ ] **Commit** - "feat: implement PresetManager for CRUD operations"

---

## Fase 3: Módulos UI

### 3.1 - eq_slider.py

- [✅] **UI.1.1** - Implementar `EQSlider.__init__()`
  - Criar widget GTK4 (Gtk.Box)
  - Adicionar label com frequência
  - Adicionar Gtk.Scale vertical com range -12 a +12
  - Adicionar label com valor em dB
  - **Status:** [✅]
  - **Estimativa:** 15 minutos

- [✅] **UI.1.2** - Implementar `EQSlider.get_value()`
  - Retornar valor atual do scale
  - **Status:** [✅]
  - **Estimativa:** 2 minutos

- [✅] **UI.1.3** - Implementar `EQSlider.set_value()`
  - Setar valor do scale
  - Atualizar label de valor
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [✅] **UI.1.4** - Implementar colorização dinâmica
  - Verde se gain > 0
  - Azul se gain < 0
  - Cinza se gain = 0
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **UI.1.5** - Implementar `connect_value_changed()`
  - Conectar sinal "value-changed" a callback
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [ ] **Commit** - "feat: implement EQSlider custom widget"

---

### 3.2 - main_window.py

- [✅] **UI.2.1** - Implementar `MainWindow.__init__()`
  - Herdar de `Adw.ApplicationWindow`
  - Inicializar managers (config, pipewire, preset)
  - Chamar `setup_ui()`
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **UI.2.2** - Implementar `MainWindow.setup_ui()`
  - Criar grid/box layout
  - Criar 10 EQSlider widgets
  - Criar dropdown de presets
  - Criar botões (Load, Save, Delete, Reset)
  - Criar status bar
  - **Status:** [✅]
  - **Estimativa:** 30 minutos

- [✅] **UI.2.3** - Implementar `MainWindow.on_slider_changed()`
  - Capturar valor do slider
  - Escrever em config
  - Gerar arquivo PipeWire
  - **Threading:** Usar `threading.Thread` para reload
  - **Thread-Safe UI:** Usar `GLib.idle_add()` para atualizar status
  - **Status:** [✅]
  - **Estimativa:** 20 minutos

- [✅] **UI.2.4** - Implementar `MainWindow.on_load_preset()`
  - Ler preset do preset_manager
  - Atualizar sliders visualmente
  - Gerar arquivo PipeWire
  - **Threading:** Recarregar em thread
  - **Status:** [✅]
  - **Estimativa:** 15 minutos

- [✅] **UI.2.5** - Implementar `MainWindow.on_save_preset()`
  - Abrir dialog pedindo nome
  - Validar nome
  - Chamar `preset_manager.save_preset()`
  - Recarregar dropdown
  - **Status:** [✅]
  - **Estimativa:** 15 minutos

- [✅] **UI.2.6** - Implementar `MainWindow.on_delete_preset()`
  - Confirmar exclusão (dialog)
  - Chamar `preset_manager.delete_preset()`
  - Recarregar dropdown
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **UI.2.7** - Implementar `MainWindow.on_reset()`
  - Resetar todos sliders para 0dB
  - Gerar arquivo PipeWire com todos 0
  - Recarregar
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **UI.2.8** - Implementar `MainWindow.refresh_preset_list()`
  - Chamar `preset_manager.list_presets()`
  - Atualizar dropdown
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [✅] **UI.2.9** - Implementar `MainWindow.update_status()`
  - Atualizar status bar com mensagem
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [ ] **Commit** - "feat: implement MainWindow UI and event handlers"

---

### 3.3 - main.py

- [✅] **UI.3.1** - Implementar `SimplePipeWireEQApp`
  - Herdar de `Adw.Application`
  - Implementar `do_activate()`
  - Chamar `PipeWireManager.setup_initial_config()` se primeira vez
  - Criar e mostrar `MainWindow`
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **UI.3.2** - Implementar `main()`
  - Criar app instance
  - Chamar `app.run(sys.argv)`
  - **Status:** [✅]
  - **Estimativa:** 5 minutos

- [ ] **Teste Manual:** Executar aplicação
  ```bash
  python3 src/simplepipewireq/main.py
  ```
  - Verificar se janela abre
  - Verificar se 10 sliders aparecem
  - Verificar se dropdown de presets funciona
  - Verificar se botões respondem
  - **Status:** [ ]
  - **Estimativa:** 10 minutos

- [ ] **Commit** - "feat: implement main entry point with first-run setup"

---

## Fase 4: Packaging e Documentação

- [✅] **Package.1** - Finalizar `requirements.txt`
  ```
  gtk4>=4.10.0
  PyGObject>=3.46.0
  libadwaita>=1.3.0
  ```
  - **Status:** [✅]
  - **Estimativa:** 2 minutos

- [✅] **Package.2** - Finalizar `setup.py`
  - Name: simplepipewireq
  - Version: 1.0.0
  - Entry point: `simplepipewireq = simplepipewireq.main:main`
  - **Status:** [✅]
  - **Estimativa:** 10 minutos

- [✅] **Package.3** - Finalizar `.gitignore`
  - Python: `__pycache__/`, `*.pyc`, `*.egg-info/`
  - Vim: `.swp`, `.swo`
  - OS: `.DS_Store`
  - **Status:** [✅]
  - **Estimativa:** 2 minutos

- [✅] **Package.4** - Escrever README.md completo
  - Descrição
  - Requisitos
  - Instalação
  - Uso
  - Troubleshooting
  - **Status:** [✅]
  - **Estimativa:** 20 minutos

- [ ] **Commit** - "docs: finalize packaging and documentation"

---

## Fase 5: Testes Finais

- [ ] **Test.1** - Executar testes unitários
  ```bash
  pytest tests/ -v
  ```
  - Todos devem passar
  - **Status:** [ ]
  - **Estimativa:** 5 minutos

- [ ] **Test.2** - Teste Manual: Primeira Execução
  - Deletar arquivo de config anterior (se existir)
  - Executar `python3 src/simplepipewireq/main.py`
  - Verificar se dialog "Configuração inicial" aparece
  - Verificar se arquivo foi criado
  - Verificar se PipeWire foi recarregado
  - **Status:** [ ]
  - **Estimativa:** 10 minutos

- [ ] **Test.3** - Teste Manual: Ajuste em Tempo Real
  - Colocar música para tocar (YouTube/Spotify)
  - Mover sliders
  - Verificar se som muda
  - Verificar se status bar atualiza
  - **Status:** [ ]
  - **Estimativa:** 10 minutos

- [ ] **Test.4** - Teste Manual: Salvamento de Preset
  - Ajustar alguns sliders
  - Clicar "Save"
  - Nomear "TestBass"
  - Verificar se arquivo foi criado
  - Verificar se aparece no dropdown
  - **Status:** [ ]
  - **Estimativa:** 5 minutos

- [ ] **Test.5** - Teste Manual: Carregamento de Preset
  - Resetar tudo
  - Carregar "TestBass"
  - Verificar se sliders voltaram às posições
  - Verificar se som volta ao tom anterior
  - **Status:** [ ]
  - **Estimativa:** 5 minutos

- [ ] **Test.6** - Teste Manual: Deleção de Preset
  - Clicar "Delete" em "TestBass"
  - Confirmar exclusão
  - Verificar se desapareceu do dropdown
  - Verificar se arquivo foi deletado
  - **Status:** [ ]
  - **Estimativa:** 5 minutos

- [ ] **Commit** - "test: add comprehensive test coverage"

---

## Status Final

- [ ] **All Phases Complete**
  - Código 100% implementado
  - Testes 100% passando
  - Documentação 100% completa
  - **Status:** [ ]

---

## Notas para o Agente

### Se Interrupção Acontecer:

1. **Ler este arquivo** — Identifique o último ✅
2. **Continuar de onde parou** — Comece no próximo [ ]
3. **Fazer commits regulares** — A cada módulo completado
4. **Atualizar este arquivo** — Marque status ao completar

### Comandos Úteis:

```bash
# Ver status do projeto
git status

# Ver último commit
git log -1

# Ver histórico de commits
git log --oneline | head -20

# Voltar a um commit anterior (se necessário)
git reset --hard <commit_hash>
```

### Problemas Comuns:

| Problema | Solução |
|----------|---------|
| "ModuleNotFoundError: No module named 'gi'" | `pip install PyGObject` |
| "systemctl: command not found" | systemd não instalado (raro no Linux) |
| "PipeWire not running" | `systemctl --user start pipewire` |
| "Audio cuts out ao testar" | Esperado! Reload interrompe áudio ~100ms |
| "Arquivo .conf corrompido" | `rm ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf` e reiniciar app |

---

**Fim do Rastreamento de Progresso**
