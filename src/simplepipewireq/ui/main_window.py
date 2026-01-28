import threading
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
from simplepipewireq.utils.constants import (
    FREQUENCIES, APP_NAME, WINDOW_WIDTH, WINDOW_HEIGHT
)
from simplepipewireq.core.config_manager import ConfigManager
from simplepipewireq.core.pipewire_manager import PipeWireManager
from simplepipewireq.core.preset_manager import PresetManager
from simplepipewireq.ui.eq_slider import EQSlider

class MainWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Managers
        self.config_manager = ConfigManager()
        self.pipewire_manager = PipeWireManager()
        self.preset_manager = PresetManager()
        
        # Estado
        self.gains = {freq: 0.0 for freq in FREQUENCIES}
        self.sliders = []
        self._reload_timer = None
        
        self.setup_ui()
        self.apply_css()
        self.refresh_preset_list()

    def setup_ui(self):
        self.set_title(APP_NAME)
        self.set_default_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        # Gerenciar Tema Dark corretamente no Libadwaita
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_DARK)
        
        # O Libadwaita AdwApplicationWindow já tem um HeaderBar interno gerenciado pelo Adw.ToolbarView.
        # Para um design limpo e moderno, vamos usar o Adw.ToolbarView como root.
        
        toolbar_view = Adw.ToolbarView()
        header = Adw.HeaderBar()
        toolbar_view.add_top_bar(header)
        
        self.set_content(toolbar_view)
        
        # Main Layout (dentro do ToolbarView)
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        toolbar_view.set_content(root_box)
        
        # Preset Toolbar
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        preset_box.set_margin_start(20)
        preset_box.set_margin_end(20)
        preset_box.set_margin_top(15)
        preset_box.set_margin_bottom(15)
        preset_box.add_css_class("card")
        
        # Preset Dropdown (StringList)
        self.preset_model = Gtk.StringList()
        self.preset_dropdown = Gtk.DropDown(model=self.preset_model)
        self.preset_dropdown.set_hexpand(True)
        self.preset_dropdown.connect("notify::selected", self.on_load_preset)
        
        preset_label = Gtk.Label(label="Preset:")
        preset_box.append(preset_label)
        preset_box.append(self.preset_dropdown)
        
        # Action Buttons
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        btn_save = Gtk.Button(label="Salvar", icon_name="document-save-symbolic")
        btn_save.connect("clicked", self.on_save_preset)
        btn_save.add_css_class("suggested-action")
        
        btn_delete = Gtk.Button(label="Deletar", icon_name="edit-delete-symbolic")
        btn_delete.connect("clicked", self.on_delete_preset)
        btn_delete.add_css_class("destructive-action")
        
        btn_reset = Gtk.Button(label="Resetar", icon_name="view-refresh-symbolic")
        btn_reset.connect("clicked", self.on_reset)
        
        btn_box.append(btn_save)
        btn_box.append(btn_delete)
        btn_box.append(btn_reset)
        preset_box.append(btn_box)
        
        root_box.append(preset_box)
        
        # Equalizer Sliders Container
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        
        # Grid para Sliders
        self.slider_grid = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.slider_grid.set_halign(Gtk.Align.CENTER)
        self.slider_grid.set_margin_start(20)
        self.slider_grid.set_margin_end(20)
        self.slider_grid.set_margin_top(20)
        self.slider_grid.set_margin_bottom(20)
        
        for i, freq in enumerate(FREQUENCIES):
            slider = EQSlider(freq)
            # Atualiza ganhos internos para salvar no preset_manager enquanto move
            slider.connect_value_changed(lambda s, val, idx=i: self.on_slider_moving(s, idx))
            # O Reload do PipeWire ocorre agora no input_finished (mouse solto)
            slider.connect_input_finished(lambda s, val, idx=i: self.on_slider_done(s, idx))
            self.sliders.append(slider)
            self.slider_grid.append(slider)
            
        scroll.set_child(self.slider_grid)
        root_box.append(scroll)
        
        # Guia para o Usuário
        self.info_banner = Adw.Banner()
        self.info_banner.set_title("Selecione 'SimplePipeWireEQ' nas configurações de som para ativar.")
        self.info_banner.set_revealed(True)
        root_box.append(self.info_banner)
        
        # Status Bar
        self.status_bar = Gtk.Label(label="Pronto")
        self.status_bar.set_halign(Gtk.Align.START)
        self.status_bar.set_margin_start(10)
        self.status_bar.set_margin_bottom(5)
        self.status_bar.add_css_class("caption")
        root_box.append(self.status_bar)

    def apply_css(self):
        css_provider = Gtk.CssProvider()
        css = """
            .gain-positive { color: #2ec27e; }
            .gain-negative { color: #3584e4; }
            .gain-neutral { color: #9a9996; }
            .numeric { font-family: monospace; font-weight: bold; }
            .card { background-color: rgba(255, 255, 255, 0.05); border-radius: 8px; padding: 10px; }
        """
        css_provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), 
            css_provider, 
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def on_slider_moving(self, slider, band_index):
        """Atualiza ganhos internos enquanto move, mas não recarrega PW."""
        value = slider.get_value()
        freq = FREQUENCIES[band_index]
        self.gains[freq] = value

    def on_slider_done(self, slider, band_index):
        """Recarrega PipeWire quando o usuário solta o slider."""
        self._do_reload()

    def _do_reload(self):
        # Limpar o timer se existisse
        if self._reload_timer:
            GLib.source_remove(self._reload_timer)
            self._reload_timer = None
        
        # Salvar config temporária
        self.config_manager.write_config("temp.conf", self.gains)
        
        # Gerar config PipeWire
        if not self.pipewire_manager.generate_pipewire_config(self.gains):
            self.update_status("Erro ao gerar configuração PipeWire")
            return
            
        # Reload em thread
        self.update_status("Aplicando ajustes...")
        thread = threading.Thread(target=self._reload_pipewire_async)
        thread.start()
        return False # Stop timer

    def _reload_pipewire_async(self):
        success = self.pipewire_manager.reload_config()
        if success:
            GLib.idle_add(self.update_status, "Equalizador aplicado")
        else:
            GLib.idle_add(self.update_status, "Falha ao recarregar PipeWire")

    def on_load_preset(self, dropdown, param):
        selected_idx = dropdown.get_selected()
        if selected_idx == Gtk.INVALID_LIST_POSITION:
            return
            
        preset_name = self.preset_model.get_string(selected_idx)
        if not preset_name:
            return

        self.update_status(f"Carregando preset: {preset_name}")
        
        # Carregar ganhos
        new_gains = self.preset_manager.get_preset_gains(preset_name)
        if not new_gains:
            return
            
        self.gains.update(new_gains)
        
        # Atualizar sliders
        for i, slider in enumerate(self.sliders):
            freq = FREQUENCIES[i]
            slider.set_value(self.gains.get(freq, 0.0))
            
        # Forçar reload
        self._do_reload()

    def on_save_preset(self, button):
        # Usando Adw.AlertDialog (moderno)
        dialog = Adw.AlertDialog(
            heading="Salvar Preset",
            body="Digite o nome para o seu preset:"
        )
        
        self.preset_entry = Gtk.Entry()
        self.preset_entry.set_placeholder_text("Ex: Meu Rock")
        self.preset_entry.set_activates_default(True) # Enter no entry executa o botão default
        dialog.set_extra_child(self.preset_entry)
        
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("save", "Salvar")
        dialog.set_default_response("save")
        dialog.set_close_response("cancel")
        
        def on_response(d, res, *args):
            if res == "save":
                name = self.preset_entry.get_text().strip()
                logger.info(f"Interface: Solicitando salvamento de preset '{name}'")
                if self.preset_manager.save_preset(name, self.gains):
                    self.refresh_preset_list()
                    self.update_status(f"Preset '{name}' salvo")
                else:
                    self.update_status("Erro ao salvar preset (nome inválido?)")
            
        dialog.choose(self, None, on_response)

    def on_delete_preset(self, button):
        selected_idx = self.preset_dropdown.get_selected()
        if selected_idx == Gtk.INVALID_LIST_POSITION:
            return
            
        name = self.preset_model.get_string(selected_idx)
        
        dialog = Adw.AlertDialog(
            heading="Deletar Preset?",
            body=f"Tem certeza que deseja deletar o preset '{name}'?"
        )
        dialog.add_response("cancel", "Cancelar")
        dialog.add_response("delete", "Deletar")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        
        def on_response(d, res, *args):
            if res == "delete":
                if self.preset_manager.delete_preset(name):
                    self.refresh_preset_list()
                    self.update_status(f"Preset '{name}' deletado")
            
        dialog.choose(self, None, on_response)

    def on_reset(self, button):
        for slider in self.sliders:
            slider.set_value(0.0)
        self.gains = {freq: 0.0 for freq in FREQUENCIES}
        self.update_status("Ganhos resetados para 0dB")
        self._do_reload()

    def refresh_preset_list(self):
        presets = self.preset_manager.list_presets()
        # Limpar modelo
        while self.preset_model.get_n_items() > 0:
            self.preset_model.remove(0)
            
        for p in presets:
            self.preset_model.append(p)

    def update_status(self, message):
        self.status_bar.set_text(message)
