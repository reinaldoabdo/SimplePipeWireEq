import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, GObject, Pango
from simplepipewireq.utils.constants import MIN_GAIN, MAX_GAIN, GAIN_STEP

class EQSlider(Gtk.Box):
    """
    Widget customizado para um slider de equalizador com label de frequência e valor.
    """
    __gsignals__ = {
        'value-changed': (GObject.SignalFlags.RUN_FIRST, None, (float,)),
    }

    def __init__(self, frequency: int):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.frequency = frequency
        
        # Label da Frequência (ex: 60Hz ou 1k)
        freq_text = f"{frequency}Hz" if frequency < 1000 else f"{frequency/1000:g}kHz"
        self.label_freq = Gtk.Label(label=freq_text)
        self.label_freq.add_css_class("caption-heading")
        self.append(self.label_freq)
        
        # Scale (Slider Vertical)
        self.adjustment = Gtk.Adjustment(
            value=0.0,
            lower=MIN_GAIN,
            upper=MAX_GAIN,
            step_increment=GAIN_STEP,
            page_increment=GAIN_STEP * 2
        )
        
        self.scale = Gtk.Scale(
            orientation=Gtk.Orientation.VERTICAL,
            adjustment=self.adjustment,
            inverted=True # Inverte para que o positivo seja para cima
        )
        self.scale.set_vexpand(True)
        self.scale.set_has_origin(True)
        self.scale.set_draw_value(False) # Vamos usar nossa própria label de valor
        
        # Conecta sinal interno do scale ao nosso sinal customizado
        self.scale.connect("value-changed", self._on_scale_value_changed)
        
        self.append(self.scale)
        
        # Label do Valor (ex: +2.5 dB)
        self.label_value = Gtk.Label(label="0.0 dB")
        self.label_value.add_css_class("numeric")
        self.append(self.label_value)
        
        # Aplica estilo inicial
        self._update_style(0.0)

    def _on_scale_value_changed(self, scale):
        value = scale.get_value()
        # Formata label: +X.X dB ou -X.X dB
        sign = "+" if value > 0 else ""
        self.label_value.set_text(f"{sign}{value:.1f} dB")
        
        self._update_style(value)
        self.emit('value-changed', value)

    def _update_style(self, value):
        """Atualiza a cor do slider baseado no valor."""
        # Remove classes antigas
        self.scale.remove_css_class("gain-positive")
        self.scale.remove_css_class("gain-negative")
        self.scale.remove_css_class("gain-neutral")
        
        if value > 0:
            self.scale.add_css_class("gain-positive")
        elif value < 0:
            self.scale.add_css_class("gain-negative")
        else:
            self.scale.add_css_class("gain-neutral")

    def get_value(self) -> float:
        """Retorna o valor atual em dB."""
        return self.scale.get_value()

    def set_value(self, value: float):
        """Define o valor em dB e atualiza visualmente."""
        self.scale.set_value(value)
        # O callback _on_scale_value_changed cuidará do resto

    def connect_value_changed(self, callback):
        """Helper para conectar o sinal de mudança de valor."""
        self.connect('value-changed', lambda widget, val: callback(widget, val))
