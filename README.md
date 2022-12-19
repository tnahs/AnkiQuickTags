# AnkiQuickTags

Tag your Anki cards quickly!

## Installation

Download and run the latest [`AnkiQuickTags.ankiaddon`][releases] release.

## Usage

QuickTags are defined in the `tags.json` file found inside the add-on's
`user_files` folder:

```plaintext
addons21/AnkiQuickTags
├── src/
└── user_files
    └── tags.json
```

### Configuration

The default `tags.json` file defines a single QuickTag--`Tag-01`--along with its
shortcut `Ctrl+Alt+T`.

```json
{
    "tags": [
        {
            "name": "Tag-01",
            "shortcut": "Ctrl+Alt+T"
        }
    ],
    "other-tags": {
        "visible": true,
        "limit": 10
    }
}
```

Shortcuts are defined by concatenating combinations of `Shift`, `Ctrl`, `Alt`
and `Meta` with a `+` sign followed by a single letter e.g. `Ctrl+Alt+T`.
Shortcuts are not case-sensitive so `ctrl+alt+t` and `CTRL+ALT+T` will bind the
same key sequence.

> Note that on macOS the key mapping is a bit different:
>
> -   `Ctrl` maps to the Command key
> -   `Meta` maps to the Control key

### Context-Menu

While reviewing and editing cards, QuickTags are added to the right-click
context-menu. Optionally, an other-tags sub-menu can be enabled which consists
of an alphabetical list of existing tags not defined as QuickTags. The number
of other-tags can be limited via the add-on's configuration.

```plaintext
┌─────────────────┐
│ Cut             │
│ Copy            │
│ Paste           │
├─────────────────┤
│ ■ Tag-01        │
│ □ Tag-02        │
│ □ Tag-03        ├───────────────┐
│ Other tags... > │ □ Other-Tag-A │
└─────────────────┤ ■ Other-Tag-B │
                  │ ■ Other-Tag-C │
                  └───────────────┘
```

## Example Config

An example config can be found at: [tnahs/anki-addon-configs:AnkiQuickTags][anki-quick-tags-config].

## Development

1. Install the required `[python-version]`. See the [Anki development][anki-dev]
   docs for more information.

    ```shell
    pyenv install [python-version]
    ```

2. Clone this repository.

    ```shell
    git clone git@github.com:tnahs/AnkiQuickTags.git
    ```

3. Set `[python-version]` as the local version:

    ```shell
    cd ./AnkiQuickTags
    pyenv local [python-version]
    ```

4. Create and enter a virtual environment:

    ```shell
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    ```

5. Install required packages:

    ```shell
    pip install -r requirements.txt
    ```

6. Set development environment variables. See
   [Anki development | Environment Variables][env-var] for more information.

    Required:

    ```shell
    export ANKI_ADDON_DEVELOPMENT=1
    ```

    Optional:

    ```shell
    export ANKIDEV=1
    export LOGTERM=1
    export DISABLE_QT5_COMPAT=1
    ```

7. Run Anki from the terminal.

    ```shell
    anki
    ```

[anki-quick-tags-config]: https://github.com/tnahs/anki-addon-configs/tree/AnkiQuickTags
[anki-dev]: https://github.com/ankitects/anki/blob/main/docs/development.md
[env-var]: https://github.com/ankitects/anki/blob/main/docs/development.md#environmental-variables
[releases]: https://github.com/tnahs/AnkiQuickTags/releases
