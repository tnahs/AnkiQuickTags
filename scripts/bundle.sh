#! /bin/zsh

# https://unix.stackexchange.com/a/115431
root=${0:A:h:h}

cd "$root/addon"

zip  \
    --recurse-paths ../bundle/anki-quick-tags.ankiaddon . \
    --exclude "**/.*" \
    --include \
        "./src/**.py" \
        "./__init__.py" \
        "./user_files/**" \
        "./manifest.json"