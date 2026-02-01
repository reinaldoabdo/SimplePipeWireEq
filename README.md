# [EN] SimplePipeWireEQ
**Minimalist 10-band parametric equalizer for PipeWire on Linux.**

> **Disclaimer:** For study purposes only. No guarantee of operation. Currently under development using AI-assisted coding and markdown specification guides.

## Features
- 10-band equalizer (-12dB to +12dB)
- Real-time audio adjustment
- Save/load custom presets
- GTK4 + Libadwaita UI
- Automatic first-run setup

## How Equalization Works
This application leverages PipeWire's `libpipewire-module-filter-chain` for high-performance audio processing:
1.  **Dynamic Configuration**: It creates a virtual output node (sink) configured with `bq_peaking` parametric filters via the `param_eq` label.
2.  **Real-time Processing**: When sliders are adjusted, the app updates the configuration file in `~/.config/pipewire/pipewire.conf.d/`.
3.  **Seamless Updates**: To apply changes without audio dropouts, the application sends a `SIGHUP` signal to the PipeWire process, forcing an instant configuration reload.

## Requirements
- Linux with PipeWire (>= 0.3.0)
- pipewire-audio (or pipewire-pulse)
- Python >= 3.10
- GTK4 development libraries

## Installation & Running
Standard installation:
```bash
pip install .
```

Development mode:
```bash
pip install -e .
simplepipewireq
```

Run directly:
```bash
PYTHONPATH=src python3 src/simplepipewireq/main.py
```

## Troubleshooting
- **PipeWire not running**: `systemctl --user start pipewire`
- **No audio changes**: Check if `pipewire-audio` is installed or if the sink is correctly selected.
- **Permission denied**: Ensure `~/.config/pipewire/` is writable.

## License
MIT

---

# [PT-BR] SimplePipeWireEQ
**Equalizador paramétrico minimalista de 10 bandas para PipeWire no Linux.**

> **Aviso:** Apenas para fins de estudo. Sem garantia de funcionamento. Em desenvolvimento através de propmpts de IA com guias em arquivos MD.

## Funcionalidades
- Equalizador de 10 bandas (-12dB a +12dB)
- Ajuste de áudio em tempo real
- Salvar/carregar presets personalizados
- Interface GTK4 + Libadwaita
- Configuração automática na primeira execução

## Como Funciona a Equalização
O aplicativo utiliza o módulo `libpipewire-module-filter-chain` do PipeWire para processamento de áudio de alta performance:
1.  **Configuração Dinâmica**: Gera um nó virtual de saída (*sink*) configurado com filtros paramétricos (`bq_peaking`) do tipo `param_eq`.
2.  **Processamento em Tempo Real**: Ao ajustar os sliders, o app sobrescreve o arquivo de configuração em `~/.config/pipewire/pipewire.conf.d/`.
3.  **Atualização sem Interrupção**: Para aplicar as mudanças instantaneamente sem interromper o áudio, o aplicativo envia um sinal `SIGHUP` ao processo do PipeWire, forçando o recarregamento imediato da configuração.

## Requisitos
- Linux com PipeWire (>= 0.3.0)
- pipewire-audio (ou pipewire-pulse)
- Python >= 3.10
- Bibliotecas de desenvolvimento do GTK4

## Instalação e Execução
Instalação padrão:
```bash
pip install .
```

Modo de desenvolvimento:
```bash
pip install -e .
simplepipewireq
```

Executar diretamente:
```bash
PYTHONPATH=src python3 src/simplepipewireq/main.py
```

## Solução de Problemas
- **PipeWire não está rodando**: `systemctl --user start pipewire`
- **Sem mudanças no áudio**: Verifique se o `pipewire-audio` está instalado ou se o sink está selecionado corretamente.
- **Permissão negada**: Certifique-se de que `~/.config/pipewire/` tem permissão de escrita.

## Licença
MIT
