__version__ = "0.2.0"

import sys


if "pytest" not in sys.modules:
    from .src.addon import AnkiQuickTags
    from .src.helpers import ConfigError, show_info

    try:
        addon = AnkiQuickTags()
    except ConfigError as error:
        show_info(str(error))
    else:
        addon.setup()
