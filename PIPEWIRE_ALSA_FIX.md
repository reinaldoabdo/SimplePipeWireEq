# Correção: PipeWire não carrega módulo ALSA

## Problema Identificado

Ao abrir a aplicação SimplePipeWireEQ, o som parou porque o PipeWire não está configurado para carregar o módulo ALSA automaticamente. Isso significa que:

- O PipeWire não cria sinks para os dispositivos de áudio físicos (ALC897 Analog, HDMI, etc.)
- O equalizador existe mas não tem para onde enviar o áudio processado
- O áudio fica "preso" no equalizador sem saída

## Diagnóstico

### Verificar se o módulo ALSA está carregado

```bash
pw-cli list-objects Module | grep -i alsa
```

Se não retornar nada, o módulo ALSA não está carregado.

### Verificar dispositivos de áudio disponíveis

```bash
# Dispositivos físicos
aplay -l

# Sinks do PipeWire
pactl list sinks short
```

Se houver dispositivos físicos mas não houver sinks correspondentes no PipeWire, o módulo ALSA não está carregado.

## Solução

### Opção 1: Carregar módulo ALSA manualmente (temporário)

```bash
# Carregar módulo ALSA
pw-cli load-module libpipewire-module-alsa

# Verificar se foi carregado
pw-cli list-objects Module | grep -i alsa

# Verificar se os sinks foram criados
pactl list sinks short
```

### Opção 2: Configurar PipeWire para carregar ALSA automaticamente (recomendado)

Crie o arquivo `~/.config/pipewire/pipewire.conf.d/10-alsa.conf`:

```lua
# Carregar módulo ALSA automaticamente
context.modules = [
    { name = libpipewire-module-alsa
        args = {
            # Opcional: especificar dispositivos específicos
            #alsa.device = "hw:0"
        }
        flags = [ ifexists nofail ]
    }
]
```

Depois recarregue o PipeWire:

```bash
# Recarregar configuração
kill -HUP $(pgrep pipewire)

# Ou reiniciar o serviço
systemctl --user restart pipewire pipewire-pulse
```

### Opção 3: Usar wireplumber (recomendado para distribuições modernas)

Muitas distribuições modernas usam o `wireplumber` como session manager, que gerencia automaticamente os dispositivos ALSA. Verifique se está instalado:

```bash
# Verificar se wireplumber está instalado
which wireplumber

# Verificar se está rodando
systemctl --user status wireplumber
```

Se não estiver instalado, instale:

```bash
# Debian/Ubuntu
sudo apt install wireplumber

# Fedora
sudo dnf install wireplumber

# Arch
sudo pacman -S wireplumber
```

E inicie o serviço:

```bash
systemctl --user enable --now wireplumber
```

## Verificação

Após aplicar a solução, verifique se os dispositivos ALSA foram criados:

```bash
# Listar todos os sinks
pactl list sinks

# Deve mostrar algo como:
# 40	effect_input.simplepipewireq	PipeWire	float32le 2ch 48000Hz	SUSPENDED
# 41	alsa_output.pci-0000_00_1f.3.analog-stereo	PipeWire	float32le 2ch 48000Hz	IDLE
# 42	alsa_output.pci-0000_01_00.1.hdmi-stereo	PipeWire	float32le 2ch 48000Hz	IDLE
```

## Teste

1. **Selecione o equalizador como saída** no seu player de áudio (Spotify, VLC, etc.)
2. **Verifique se o áudio sai** nos alto-falantes
3. **Ajuste os sliders** do equalizador
4. **Verifique se as mudanças são aplicadas** sem interromper o áudio

## Solução de Problemas

### O módulo ALSA não carrega

Verifique se o PipeWire foi compilado com suporte a ALSA:

```bash
pw-cli --version
# Verifique se há suporte a ALSA na saída
```

Se não houver suporte, instale o PipeWire com suporte a ALSA:

```bash
# Debian/Ubuntu
sudo apt install pipewire pipewire-alsa

# Fedora
sudo dnf install pipewire pipewire-alsa

# Arch
sudo pacman -S pipewire pipewire-alsa
```

### Os sinks ALSA aparecem mas não há áudio

Verifique se o volume está mudo:

```bash
# Verificar volume dos sinks
pactl list sinks | grep -A 10 "Volume:"

# Aumentar volume
pactl set-sink-volume <sink_name> 100%
```

### O equalizador não aparece na lista de dispositivos

Verifique se o arquivo de configuração existe:

```bash
cat ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf
```

Se não existir, execute o setup inicial da aplicação SimplePipeWireEQ.

## Conclusão

O problema do som parar não é causado pela implementação de hot-reload do SimplePipeWireEQ, mas sim pela falta de configuração do PipeWire para carregar o módulo ALSA automaticamente. Após configurar o PipeWire corretamente, o equalizador funcionará normalmente e o áudio será processado e enviado para os dispositivos de saída físicos.
