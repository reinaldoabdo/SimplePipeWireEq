# SimplePipeWireEQ - Início Imediato (Git Já Configurado)

**Status:** Git ✅ Inicializado  
**Próximo Passo:** Começar Fase 1 (Setup Inicial)

---

## ⚡ Resumo Executivo para o Agente

Você tem **4 documentos de referência:**

1. **SimplePipeWireEQ_SPECIFICATION.md** — Especificação completa do projeto
2. **PIPEWIRE_INTEGRATION_GUIDE.md** — Guia técnico de implementação
3. **PROGRESS.md** — Checklist detalhado com estimativas de tempo
4. **GIT_CHECKPOINT_GUIDE.md** — Como recuperar se houver falha

**Leia nesta ordem:**
```
SPECIFICATION (5 min) → Entender o projeto
    ↓
PROGRESS.md (2 min) → Ver checklist completo
    ↓
Começar Fase 1 → Implementação
```

---

## 🚀 Comece Aqui (Fase 1: Setup Inicial)

### 1. Criar Estrutura de Diretórios

```bash
cd SimplePipeWireEQ/

# Criar pastas
mkdir -p src/simplepipewireq/{core,ui,utils}
mkdir -p tests
mkdir -p data

# Verificar resultado
ls -la src/simplepipewireq/
# Deve mostrar: core, ui, utils
```

### 2. Criar Arquivos __init__.py

```bash
# Em cada pasta
touch src/simplepipewireq/__init__.py
touch src/simplepipewireq/core/__init__.py
touch src/simplepipewireq/ui/__init__.py
touch src/simplepipewireq/utils/__init__.py
touch tests/__init__.py

# Conteúdo mínimo para cada:
cat > src/simplepipewireq/__init__.py << 'EOF'
"""SimplePipeWireEQ - Minimalist 10-band equalizer for PipeWire"""

__version__ = "1.0.0"
__author__ = "Your Name"
EOF
```

### 3. Criar Arquivos de Configuração

**requirements.txt:**
```bash
cat > requirements.txt << 'EOF'
gtk4>=4.10.0
PyGObject>=3.46.0
libadwaita>=1.3.0
EOF
```

**setup.py:**
```bash
cat > setup.py << 'EOF'
from setuptools import setup, find_packages

setup(
    name="simplepipewireq",
    version="1.0.0",
    description="Minimalist 10-band parametric equalizer for PipeWire",
    author="Your Name",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "simplepipewireq=simplepipewireq.main:main",
        ],
    },
    install_requires=[
        "gtk4>=4.10.0",
        "PyGObject>=3.46.0",
        "libadwaita>=1.3.0",
    ],
    python_requires=">=3.10",
)
EOF
```

**.gitignore:**
```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Testing
.pytest_cache/
.coverage
htmlcov/

# Application data
*.conf
!99-simplepipewireq.conf
EOF
```

**README.md (versão inicial):**
```bash
cat > README.md << 'EOF'
# SimplePipeWireEQ

Minimalist 10-band parametric equalizer for PipeWire on Linux.

## Features

- 10-band equalizer (-12dB to +12dB)
- Real-time audio adjustment
- Save/load custom presets
- GTK4 + Libadwaita UI
- Automatic first-run setup

## Requirements

- Linux with PipeWire
- pipewire >= 0.3.0
- pipewire-audio (or pipewire-pulse)
- Python >= 3.10
- GTK4 development libraries

## Installation

```bash
pip install -r requirements.txt
python setup.py install
```

Or run directly:
```bash
python src/simplepipewireq/main.py
```

## Usage

Start the application and adjust the 10 frequency bands.
Changes apply in real-time to your audio output.

Save custom presets for quick access to favorite EQ settings.

## Troubleshooting

- PipeWire not running: `systemctl --user start pipewire`
- No audio changes: Check if pipewire-audio is installed
- Permission denied: Ensure ~/.config/pipewire/ is writable

## License

MIT
EOF
```

### 4. Fazer Primeiro Commit

```bash
git add -A
git commit -m "chore: initialize project structure with configuration files"

# Verificar
git log --oneline | head -1
```

---

## 📚 Próximas Fases (Reference)

### Fase 2: Módulos Core
1. constants.py (5 min)
2. config_manager.py (40 min total)
3. pipewire_manager.py (50 min total)
4. preset_manager.py (40 min total)

### Fase 3: Interface GTK4
1. eq_slider.py (35 min)
2. main_window.py (75 min)
3. main.py (15 min)

### Fase 4: Packaging
1. Finalizar requirements.txt (2 min)
2. Finalizar setup.py (10 min)
3. Finalizar README.md (20 min)

### Fase 5: Testing
1. Testes unitários (pytest)
2. Testes manuais (6 cenários)

---

## 📝 Comando Essencial: Atualizar PROGRESS.md

**Após completar CADA item de PROGRESS.md:**

```bash
# 1. Marcar no arquivo (editor de texto)
#    Mude [ ] para [✅]

# 2. Commitar o progresso
git add PROGRESS.md
git commit -m "docs: mark <item> as complete"
```

---

## 🔄 Padrão Diário

```
Manhã:
  1. Ler PROGRESS.md - ver onde parou
  2. Continuar de onde parou
  3. A cada módulo: commit + atualizar PROGRESS.md

Noite (ou fim de sessão):
  1. git log --oneline | head -5  (verificar commits)
  2. git status (ver mudanças pendentes)
  3. Se tudo ok: Pode desligar
  4. Se incompleto: Fazer commit mesmo que parcial
```

---

## ⚠️ Regras Importantes

### ✅ Faça isso:

- Commit após cada função
- Mensagens descritivas
- Atualizar PROGRESS.md
- Teste após cada módulo

### ❌ Nunca:

- Pular fases
- Fazer commits genéricos ("fix", "update")
- Esquecer de testar
- Perder rastreamento em PROGRESS.md

---

## 🎯 Próximo Comando

Leia PROGRESS.md completo:

```bash
cat PROGRESS.md
```

Depois comece Fase 1 (Setup) ou Fase 2 (Core Modules) conforme apropriado.

---

## 📞 Referência Rápida

| Preciso de | Comando |
|------------|---------|
| Ver onde parei | `git log --oneline \| head -5` |
| Ver mudanças | `git status` |
| Fazer commit | `git add -A && git commit -m "..."` |
| Ver histórico | `git log --oneline \| head -20` |
| Voltar (CUIDADO) | `git reset --hard <hash>` |

---

**Você está pronto!** 

Próximo passo: Leia **PROGRESS.md** e escolha começar em **Fase 1** ou **Fase 2**.
