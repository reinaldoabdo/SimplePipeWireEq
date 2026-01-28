import sys
import logging
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw, GLib
from simplepipewireq.core.pipewire_manager import PipeWireManager
from simplepipewireq.ui.main_window import MainWindow

# Configuração básica de logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class SimplePipeWireEQApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.github.simplepipewireq")
        self.pw_manager = PipeWireManager()

    def do_activate(self):
        """Ativado quando o app é iniciado."""
        # Verificar e configurar PipeWire se necessário
        if not self.pw_manager.is_configured():
            logger.info("Configuração inicial não encontrada, criando...")
            # Setup inicial em background para não travar a UI se demorar
            self._do_initial_setup()
        
        # Criar janela principal
        window = MainWindow(application=self)
        window.present()

    def _do_initial_setup(self):
        # Dialog informativo se for a primeira vez usando Adw.AlertDialog
        def show_dialog():
            win = self.get_active_window()
            if not win: return
            
            dialog = Adw.AlertDialog(
                heading="Configuração Inicial",
                body="O SimplePipeWireEQ precisa configurar o filtro do PipeWire pela primeira vez. O áudio pode ser interrompido brevemente."
            )
            dialog.add_response("ok", "OK, entendo")
            
            def on_response(d, res, *args):
                if self.pw_manager.setup_initial_config():
                    logger.info("Setup inicial concluído")
                else:
                    logger.error("Falha no setup inicial")
                
            dialog.choose(win, None, on_response)
            
        GLib.idle_add(show_dialog)

def main():
    """Entry point da aplicação."""
    app = SimplePipeWireEQApp()
    return app.run(sys.argv)

if __name__ == "__main__":
    main()
