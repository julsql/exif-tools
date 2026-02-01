#!/usr/bin/env python3
import re


def read_version():
    with open('version.txt', 'r') as f:
        return f.read().strip()


def update_file(filepath, pattern, replacement):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    new_content = re.sub(pattern, replacement, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def main():
    version = read_version()
    print(f"Mise à jour vers la version {version}")

    # Modifier le README
    update_file(
        'README.md',
        r'Version : [\d\.]+',
        f'Version : {version}'
    )

    # Modifier la popup
    update_file(
        'editor/menu.py',
        r'Version [\d\.]+',
        f'Version {version}'
    )

    # Modifier la recherche de mise à jour
    update_file(
        'main.py',
        r"VERSION = '[\d\.]+'",
        f"VERSION = '{version}'"
    )

    # Modifier les scripts
    update_file(
        'scripts/install-all.sh',
        r'VERSION="[\d\.]+"',
        f'VERSION="{version}"'
    )
    update_file(
        'scripts/install-arm64.sh',
        r'VERSION="[\d\.]+"',
        f'VERSION="{version}"'
    )
    update_file(
        'scripts/install-mac.sh',
        r'VERSION="[\d\.]+"',
        f'VERSION="{version}"'
    )


if __name__ == '__main__':
    main()
