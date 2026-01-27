# SimplePipeWireEQ - Sistema de Checkpoint com Git

## Objetivo

Se o Agente for interrompido (falta de energia, timeout, etc), ele pode:
1. Ler `PROGRESS.md` para ver o que foi feito
2. Ler commits Git para entender o estado do código
3. Continuar exatamente de onde parou

---

## Setup Inicial de Git

### Quando começar o projeto:

```bash
cd SimplePipeWireEQ/
git init
git config user.name "SimplePipeWireEQ Agent"
git config user.email "agent@simplepipewireq"

# Criar primeiro commit com estrutura
git add -A
git commit -m "chore: initialize project structure"
```

### Verificar configuração:

```bash
git config --list | grep user
```

---

## Fluxo de Commit (Obrigatório para Cada Módulo)

### Após completar CADA item em PROGRESS.md:

```bash
# 1. Ver o que mudou
git status

# 2. Adicionar arquivos
git add -A

# 3. Fazer commit com mensagem descritiva
git commit -m "feat: implement <module>.<function> - <descrição>"

# 4. Atualizar PROGRESS.md
# (editar e marcar [✅] no item completado)

# 5. Fazer commit do progresso
git add PROGRESS.md
git commit -m "docs: update progress - <module> complete"
```

---

## Convenção de Mensagens de Commit

### Prefixos:

| Prefixo | Uso | Exemplo |
|---------|-----|---------|
| `feat:` | Nova funcionalidade | `feat: implement ConfigManager.write_config()` |
| `fix:` | Correção de bug | `fix: handle missing config directory` |
| `test:` | Testes | `test: add unit tests for preset_manager` |
| `docs:` | Documentação | `docs: update README with installation steps` |
| `chore:` | Tarefas administrativas | `chore: update .gitignore` |
| `refactor:` | Refatoração | `refactor: simplify preset validation logic` |

### Formato:

```
<tipo>: <descrição curta>

<descrição longa opcional>
<detalhes técnicos>
<números de linhas de código>
```

### Exemplos Reais:

```bash
# Simples
git commit -m "feat: implement constants.py with frequencies"

# Com descrição
git commit -m "feat: implement PipeWireManager.generate_pipewire_config()

- Generates valid Lua configuration for PipeWire filter-chain
- Supports all 10 frequency bands with dynamic gains
- Creates ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
- Tested with manual verification of Lua syntax"

# Fix com detalhes
git commit -m "fix: handle missing directory in config_manager

Previously crashed if ~/.config/pipewire/ didn't exist.
Now creates it automatically with proper permissions.
Fixes issue reported in tests."
```

---

## Comandos Git Essenciais para Recuperação

### Ver o que foi feito:

```bash
# Últimos 10 commits
git log --oneline | head -10

# Commits de hoje
git log --since="1 day ago" --oneline

# Commit específico
git show <commit_hash>

# Diferença desde último commit
git diff
```

### Voltar a um ponto anterior (se necessário):

```bash
# Resetar para estado anterior (CUIDADO!)
git reset --hard <commit_hash>

# Ver histórico antes de resetar
git reflog
```

### Checar qual módulo estava sendo trabalhado:

```bash
# Ver qual arquivo foi modificado por último
git log --name-only | head -20

# Ver qual módulo foi commitado por último
git log --oneline | grep -i "Core\|UI\|feat" | head -5
```

---

## Checkpoint Automático após Cada Fase

### Fase 1 (Setup):
```bash
git commit -m "chore: complete project initialization

- Directory structure created
- Initial __init__.py files added
- requirements.txt, setup.py, .gitignore configured
- README template created"
```

### Fase 2 (Core Modules):

Após CADA módulo core:
```bash
git commit -m "feat: implement <module_name>

Core functionality for <brief description>
Functions: <list of functions>
Tests: Passing"
```

Exemplo:
```bash
git commit -m "feat: implement config_manager module

Handles reading/writing INI configuration files.
Functions: read_config, write_config, validate_gain
Status: Unit tests passing (100%)"
```

### Fase 3 (UI Modules):
```bash
git commit -m "feat: implement <widget_name> UI component

Custom GTK4 widget for <purpose>
Features: <list of features>
Integrated with: <connected modules>"
```

### Fase 4 (Packaging):
```bash
git commit -m "chore: finalize packaging and metadata

- requirements.txt dependencies confirmed
- setup.py entry points configured
- .gitignore comprehensive
- README complete with instructions"
```

### Fase 5 (Testing):
```bash
git commit -m "test: comprehensive testing complete

- Unit tests: 100% passing
- Manual verification: All 6 scenarios passed
- First-run setup: Confirmed working
- Real-time adjustment: Verified with audio
- Preset management: Save/load/delete working"
```

---

## Recuperação Após Interrupção

### Cenário 1: Agente morreu no meio de um módulo

**Procedimento:**

1. **Checar status**
   ```bash
   git status
   git log --oneline | head -5
   ```

2. **Ler PROGRESS.md**
   - Identifique o último ✅
   - O que está em [🔄]?

3. **Opções:**

   **Opção A:** Continuar o trabalho
   ```bash
   # Ver qual arquivo está incompleto
   git diff
   
   # Completar a implementação
   # (editar arquivos)
   
   # Fazer commit quando pronto
   git add -A
   git commit -m "feat: complete <module> implementation"
   ```

   **Opção B:** Descartar e recomeçar
   ```bash
   # Voltar ao último commit bem-sucedido
   git reset --hard <commit_hash_anterior>
   
   # Continuar de lá
   ```

---

### Cenário 2: Não sabe onde parou

**Procedimento:**

1. **Ver histórico completo**
   ```bash
   git log --oneline --all
   ```

2. **Ver PROGRESS.md**
   ```bash
   cat PROGRESS.md | grep "✅\|🔄\|❌"
   ```

3. **Identificar fase atual**
   - Se muitos ✅ em Fase 2 → Está em Fase 3
   - Se muitos ✅ em Fase 3 → Está em Fase 4
   - etc

4. **Ler últimos 3 commits**
   ```bash
   git log --oneline | head -3
   ```

5. **Continuar do próximo item não marcado**

---

### Cenário 3: Código está quebrado

**Procedimento:**

```bash
# 1. Ver último commit que funcionava
git log --oneline | head -10

# 2. Voltar a esse commit
git reset --hard <commit_hash>

# 3. Recomeçar de lá
# (será mais lento, mas garantido de funcionar)

# 4. Após voltar, refaça com mais cuidado
```

---

## Estrutura de Commits Esperados

### Se o projeto for implementado corretamente, histórico será:

```
feat: implement main entry point with first-run setup
feat: implement MainWindow UI and event handlers
feat: implement EQSlider custom widget
feat: implement PresetManager for CRUD operations
feat: implement PipeWireManager for Lua generation and reloading
feat: implement ConfigManager for INI file handling
feat: add constants module with frequencies and paths
chore: create project structure and initialization files
chore: initialize project with git
```

(De baixo para cima no tempo)

### Contar commits:

```bash
# Deve haver ~35-40 commits se tudo foi bem
git log --oneline | wc -l
```

---

## Verificação Rápida de Status

### Criar um "status check" rápido:

```bash
#!/bin/bash
echo "=== SimplePipeWireEQ Status ==="
echo ""
echo "Total Commits:"
git log --oneline | wc -l
echo ""
echo "Last 5 Commits:"
git log --oneline | head -5
echo ""
echo "Files Modified:"
git diff --name-only
echo ""
echo "Branch:"
git branch
echo ""
echo "=== PROGRESS.md Status ==="
grep "✅\|🔄\|❌" PROGRESS.md | head -10
```

Salvar como `status.sh` e executar:
```bash
bash status.sh
```

---

## Boas Práticas

### ✅ Faça isso:

- Commit após CADA função completada
- Use mensagens descritivas
- Atualizar PROGRESS.md antes de cada commit
- Fazer commit de PROGRESS.md também

### ❌ Não faça:

- Commits muito grandes com múltiplos módulos
- Mensagens genéricas como "fix stuff" ou "working"
- Esquecer de fazer commit antes de interrupção
- Resetar sem checar o que vai perder

---

## Integração com PROGRESS.md

### Cada item em PROGRESS.md deve ter status:

```markdown
- [ ] **Core.1.1** - Implementar `constants.py`
  - **Status:** [ ]  ← Mude para ✅ ou 🔄
  - **Commit:** (copie hash do commit relevante)
```

### Exemplo atualizado:

```markdown
- [✅] **Core.1.1** - Implementar `constants.py`
  - **Status:** ✅
  - **Commit:** a1b2c3d "feat: add constants module with frequencies and paths"
```

---

## Cenário Real: Recuperação Completa

### Dia 1: Agente trabalha por 2 horas

```bash
git log --oneline
# a1b2c3d feat: implement ConfigManager.write_config()
# 9e8f7g6 feat: implement ConfigManager.__init__()
# 1h2i3j4 feat: add constants module
# ...
```

**PROGRESS.md mostra:**
```
Core.1.1 ✅
Core.2.1 ✅
Core.2.2 ✅
Core.2.3 [🔄] (em andamento)
```

### Dia 2: Energia voltou. Agente retoma:

```bash
# 1. Ver onde parou
cat PROGRESS.md | grep -A5 "🔄"

# 2. Ver último commit
git log -1

# 3. Ver código incompleto
git status

# 4. Continuar exatamente de onde parou
# (editar Core.2.3 - read_config)

# 5. Quando pronto
git add -A
git commit -m "feat: implement ConfigManager.read_config()"

# 6. Marcar como completo
# (editar PROGRESS.md: Core.2.3 ✅)

# 7. Continuar com Core.2.4
```

---

## TL;DR - Quick Reference

```bash
# Iniciar projeto
git init
git config user.name "SimplePipeWireEQ Agent"

# Após completar cada item
git add -A
git commit -m "feat: implement <module>.<function>"

# Se interrompido
git log --oneline | head -5  # Ver onde parou
cat PROGRESS.md             # Ver checklist
git reset --hard <hash>     # Voltar se necessário
git diff                    # Ver mudanças

# Recuperar
git reflog                  # Ver tudo que fez
git checkout <branch>       # Voltar se mudou de branch
```

---

**Fim das Instruções de Git e Checkpoint**
