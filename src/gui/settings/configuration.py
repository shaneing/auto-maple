import logging
import tkinter as tk
from src.gui.interfaces import LabelFrame, Frame
from src.common.interfaces import Configurable
from src.logger import set_log_level

_logger = logging.getLogger(__name__)


class Configuration(LabelFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, 'Configuration', **kwargs)

        self.configuration_settings = ConfigurationSettings('configuration')
        self.debug = tk.BooleanVar(value=self.configuration_settings.get('DEBUG'))
        self._debug_on_change()

        debug_row = Frame(self)
        debug_row.pack(side=tk.TOP, fill='x', expand=True, pady=5, padx=5)
        check = tk.Checkbutton(
            debug_row,
            variable=self.debug,
            text='debug',
            command=self._debug_on_change,
            onvalue=True,
            offvalue=False,
        )
        check.pack()

        # num_row = Frame(self)
        # num_row.pack(side=tk.TOP, fill='x', expand=True, pady=(0, 5), padx=5)
        # label = tk.Label(num_row, text='Number of pets to feed:')
        # label.pack(side=tk.LEFT, padx=(0, 15))
        # radio_group = Frame(num_row)
        # radio_group.pack(side=tk.LEFT)

    def _debug_on_change(self):
        if self.debug.get():
            set_log_level("DEBUG")
            _logger.debug("Opened debug")
        else:
            set_log_level("INFO")

        self.configuration_settings.set('DEBUG', self.debug.get())
        self.configuration_settings.save_config()


class ConfigurationSettings(Configurable):
    DEFAULT_CONFIG = {
        'DEBUG': False,
    }

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        assert key in self.config
        self.config[key] = value
