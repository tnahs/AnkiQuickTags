import sys

from .src import AnkiQuickTags, errors

try:
    addon = AnkiQuickTags()
except errors.ConfigError as error:
    # Prevents AnkiQuickTags from hooking to Anki if there are any config
    # errors. See `AnkiQuickTags._validate_config()`
    sys.stderr.write(f"{AnkiQuickTags.name}: {error}")
else:
    addon.setup()
