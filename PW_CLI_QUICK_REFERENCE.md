# Guia Rápido: Comandos pw-cli para Atualização Dinâmica

## Visão Geral

Este guia fornece comandos específicos do `pw-cli` para manipular dinamicamente os parâmetros do equalizador PipeWire sem reiniciar o daemon.

## Comandos Básicos

### Listar Objetos

```bash
# Listar todos os nós
pw-cli list-objects Node

# Listar todos os módulos
pw-cli list-objects Module

# Listar todas as portas
pw-cli list-objects Port

# Listar todos os links
pw-cli list-objects Link

# Listar todos os clientes
pw-cli list-objects Client
```

### Monitorar Eventos

```bash
# Monitorar todos os eventos em tempo real
pw-cli monitor

# Monitorar eventos de um nó específico
pw-cli monitor <node_id>

# Monitorar eventos de um módulo específico
pw-cli monitor <module_id>
```

## Manipulação de Módulos

### Encontrar Módulo filter-chain

```bash
# Listar módulos e encontrar o filter-chain
pw-cli list-objects Module | grep filter-chain

# Saída esperada:
#	id 45
#		type PipeWire:Interface:Module
#		module.name "libpipewire-module-filter-chain"
```

### Descarregar Módulo

```bash
# Descarregar módulo pelo ID
pw-cli unload-module 45

# Verificar se foi descarregado
pw-cli list-objects Module | grep filter-chain
```

### Carregar Módulo

```bash
# Carregar módulo filter-chain com configuração
pw-cli load-module libpipewire-module-filter-chain \
  'node.description="SimplePipeWireEQ Equalizer Sink" \
   media.name="SimplePipeWireEQ Equalizer Sink" \
   filter.graph={ nodes=[ { type=builtin, name=eq, label=param_eq, config={ filters=[ { type=bq_peaking, freq=1000, gain=0.0, q=0.707 } ] } } ] inputs=[ "eq:In 1" "eq:In 2" ] outputs=[ "eq:Out 1" "eq:Out 2" ] } \
   capture.props={ node.name="effect_input.simplepipewireq" media.class="Audio/Sink" audio.channels=2 audio.position=[ FL FR ] } \
   playback.props={ node.name="effect_output.simplepipewireq" node.passive=true audio.channels=2 audio.position=[ FL FR ] }'
```

## Manipulação de Nós

### Encontrar Nó do Equalizador

```bash
# Listar nós e encontrar o equalizador
pw-cli list-objects Node | grep -A 10 "SimplePipeWireEQ"

# Saída esperada:
#	id 67
#		type PipeWire:Interface:Node
#		node.name "effect_input.simplepipewireq"
#		node.description "SimplePipeWireEQ Equalizer Sink"
#		media.class "Audio/Sink"
#		audio.channels 2
#		audio.position [ FL FR ]
```

### Enumerar Parâmetros de um Nó

```bash
# Enumerar todos os parâmetros de Props
pw-cli enum-params 67 Props

# Enumerar parâmetros de Format
pw-cli enum-params 67 Format

# Enumerar parâmetros de Buffer
pw-cli enum-params 67 Buffer
```

### Definir Parâmetros de um Nó

```bash
# Definir volume (canais estéreo)
pw-cli set-param 67 Props '{ channelVolumes: [ 1.0, 1.0 ] }'

# Definir volume com boost (+6dB = 2.0x)
pw-cli set-param 67 Props '{ channelVolumes: [ 2.0, 2.0 ] }'

# Definir volume com atenuação (-6dB = 0.5x)
pw-cli set-param 67 Props '{ channelVolumes: [ 0.5, 0.5 ] }'

# Definir mudo
pw-cli set-param 67 Props '{ mute: true }'

# Remover mudo
pw-cli set-param 67 Props '{ mute: false }'

# Definir nome do nó
pw-cli set-param 67 Props '{ node.name: "novo_nome" }'

# Definir descrição do nó
pw-cli set-param 67 Props '{ node.description: "Nova Descrição" }'
```

## Manipulação de Portas

### Listar Portas de um Nó

```bash
# Listar todas as portas
pw-cli list-objects Port

# Listar portas de entrada de um nó específico
pw-cli list-objects Port | grep "node.id 67" | grep "direction in"

# Listar portas de saída de um nó específico
pw-cli list-objects Port | grep "node.id 67" | grep "direction out"
```

### Conectar Portas

```bash
# Listar portas disponíveis
pw-link -o  # Portas de saída
pw-link -i  # Portas de entrada

# Conectar duas portas
pw-link <output_port_id> <input_port_id>

# Conectar por nome
pw-link "alsa_output.pci-0000_00_1f.3.analog-stereo:monitor_FL" \
        "effect_input.simplepipewireq:In 1"

# Desconectar portas
pw-link -d <output_port_id> <input_port_id>

# Desconectar todas as conexões de uma porta
pw-link -d <port_id>
```

## Recarregamento de Configuração

### Método 1: SIGHUP (Recomendado)

```bash
# Enviar SIGHUP para recarregar configuração
kill -HUP $(pgrep pipewire)

# Verificar se recarregou com sucesso
pw-cli list-objects Node | grep SimplePipeWireEQ
```

### Método 2: Restart pipewire-pulse

```bash
# Reiniciar apenas pipewire-pulse (menos disruptivo)
systemctl --user restart pipewire-pulse

# Verificar status
systemctl --user status pipewire-pulse
```

### Método 3: Recarregar Módulo filter-chain

```bash
# 1. Encontrar ID do módulo
MODULE_ID=$(pw-cli list-objects Module | grep filter-chain | grep -oP 'id \K\d+')

# 2. Descarregar módulo
pw-cli unload-module $MODULE_ID

# 3. Recarregar configuração
kill -HUP $(pgrep pipewire)

# 4. Verificar se nó foi recriado
pw-cli list-objects Node | grep SimplePipeWireEQ
```

## Scripts Úteis

### Script: Recarregar Equalizador

```bash
#!/bin/bash
# reload_eq.sh - Recarrega o equalizador PipeWire

echo "Recarregando equalizador..."

# 1. Encontrar módulo filter-chain
MODULE_ID=$(pw-cli list-objects Module | grep filter-chain | grep -oP 'id \K\d+')

if [ -z "$MODULE_ID" ]; then
    echo "Módulo filter-chain não encontrado, carregando..."
else
    echo "Descarregando módulo filter-chain (ID: $MODULE_ID)..."
    pw-cli unload-module $MODULE_ID
    sleep 0.2
fi

# 2. Recarregar configuração
echo "Recarregando configuração PipeWire..."
kill -HUP $(pgrep pipewire)
sleep 0.5

# 3. Verificar se nó foi recriado
NODE_ID=$(pw-cli list-objects Node | grep SimplePipeWireEQ | grep -oP 'id \K\d+')

if [ -n "$NODE_ID" ]; then
    echo "✓ Equalizador recarregado com sucesso (nó ID: $NODE_ID)"
else
    echo "✗ Falha ao recarregar equalizador"
    exit 1
fi
```

### Script: Definir Volume do Equalizador

```bash
#!/bin/bash
# set_eq_volume.sh - Define o volume do equalizador

if [ -z "$1" ]; then
    echo "Uso: $0 <volume_dB>"
    echo "Exemplo: $0 3.0  (+3dB)"
    echo "         $0 -2.5 (-2.5dB)"
    exit 1
fi

VOLUME_DB=$1

# Converter dB para fator de amplitude
# amplitude = 10^(dB/20)
VOLUME=$(python3 -c "print(10 ** ($VOLUME_DB / 20.0))")

# Encontrar nó do equalizador
NODE_ID=$(pw-cli list-objects Node | grep SimplePipeWireEQ | grep -oP 'id \K\d+')

if [ -z "$NODE_ID" ]; then
    echo "✗ Nó do equalizador não encontrado"
    exit 1
fi

# Definir volume
echo "Definindo volume para $VOLUME_DB dB (fator: $VOLUME)..."
pw-cli set-param $NODE_ID Props "{ channelVolumes: [ $VOLUME, $VOLUME ] }"

if [ $? -eq 0 ]; then
    echo "✓ Volume definido com sucesso"
else
    echo "✗ Falha ao definir volume"
    exit 1
fi
```

### Script: Monitorar Equalizador

```bash
#!/bin/bash
# monitor_eq.sh - Monitora o estado do equalizador

echo "Monitorando equalizador SimplePipeWireEQ..."
echo "Pressione Ctrl+C para sair"
echo ""

while true; do
    # Encontrar nó
    NODE_ID=$(pw-cli list-objects Node | grep SimplePipeWireEQ | grep -oP 'id \K\d+')
    
    if [ -n "$NODE_ID" ]; then
        # Obter estado
        STATE=$(pw-cli info $NODE_ID 2>/dev/null | grep "state" | grep -oP '"\K[^"]+')
        
        # Obter volume
        VOLUME=$(pw-cli enum-params $NODE_ID Props 2>/dev/null | grep "channelVolumes" | grep -oP '\[\K[^\]]+')
        
        echo "[$(date +%H:%M:%S)] Nó ID: $NODE_ID | Estado: $STATE | Volume: [$VOLUME]"
    else
        echo "[$(date +%H:%M:%S)] ✗ Nó do equalizador não encontrado"
    fi
    
    sleep 2
done
```

## Debugging

### Verificar Logs do PipeWire

```bash
# Ver logs em tempo real
journalctl --user -u pipewire -f

# Ver logs do pipewire-pulse
journalctl --user -u pipewire-pulse -f

# Ver logs com filtro
journalctl --user -u pipewire | grep -i "filter-chain"
journalctl --user -u pipewire | grep -i "simplepipewireq"
```

### Verificar Configuração Carregada

```bash
# Ver arquivo de configuração
cat ~/.config/pipewire/pipewire.conf.d/99-simplepipewireq.conf

# Ver configuração completa do PipeWire
pw-cli dump 0
```

### Testar Áudio

```bash
# Reproduzir arquivo de teste
pw-play /usr/share/sounds/alsa/Front_Center.wav

# Reproduzir tom de teste
pw-play /usr/share/sounds/freedesktop/stereo/complete.oga

# Gravar áudio
pw-record /tmp/test.wav
```

## Referência de Parâmetros

### Props (Propriedades do Nó)

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `channelVolumes` | Array[float] | Volume de cada canal (0.0 a 4.0) |
| `mute` | Boolean | Estado de mudo |
| `node.name` | String | Nome do nó |
| `node.description` | String | Descrição do nó |
| `media.class` | String | Classe de mídia (ex: "Audio/Sink") |
| `audio.channels` | Int | Número de canais de áudio |
| `audio.position` | Array[String] | Posição dos canais (ex: [FL, FR]) |

### Format (Formato de Áudio)

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `mediaType` | String | Tipo de mídia ("audio") |
| `mediaSubtype` | String | Subtipo ("raw") |
| `format` | String | Formato ("S16LE", "S32LE", "F32LE") |
| `rate` | Int | Taxa de amostragem (44100, 48000, etc.) |
| `channels` | Int | Número de canais |
| `position` | Array[String] | Posição dos canais |

### Buffer (Buffer de Áudio)

| Parâmetro | Tipo | Descrição |
|-----------|------|-----------|
| `maxBufferSize` | Int | Tamanho máximo do buffer |
| `latency` | Object | Latência (min, max) |
| `size` | Int | Tamanho do buffer |

## Conversão de dB para Fator de Amplitude

```python
# dB para fator de amplitude
amplitude = 10 ** (dB / 20.0)

# Exemplos:
# +12 dB = 10^(12/20) = 3.98
# +6 dB  = 10^(6/20)  = 2.00
# +3 dB  = 10^(3/20)  = 1.41
# 0 dB   = 10^(0/20)  = 1.00
# -3 dB  = 10^(-3/20) = 0.71
# -6 dB  = 10^(-6/20) = 0.50
# -12 dB = 10^(-12/20)= 0.25
```

## Tabela de Referência Rápida

| Ação | Comando |
|------|---------|
| Listar nós | `pw-cli list-objects Node` |
| Listar módulos | `pw-cli list-objects Module` |
| Encontrar EQ | `pw-cli list-objects Node \| grep SimplePipeWireEQ` |
| Descarregar módulo | `pw-cli unload-module <id>` |
| Definir volume | `pw-cli set-param <id> Props '{ channelVolumes: [1.0, 1.0] }'` |
| Mudo | `pw-cli set-param <id> Props '{ mute: true }'` |
| Recarregar config | `kill -HUP $(pgrep pipewire)` |
| Monitorar | `pw-cli monitor` |
| Listar portas | `pw-cli list-objects Port` |
| Conectar portas | `pw-link <out> <in>` |
| Desconectar | `pw-link -d <out> <in>` |

## Conclusão

Este guia fornece comandos específicos e práticos para manipular dinamicamente os parâmetros do equalizador PipeWire usando `pw-cli`. Para mais informações, consulte:

- Documentação do PipeWire: https://docs.pipewire.org/
- Man pages: `man pw-cli`, `man pw-link`, `man pw-mon`
- Código fonte do PipeWire: https://gitlab.freedesktop.org/pipewire/pipewire
