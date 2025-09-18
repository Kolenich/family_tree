"""Script for bumping version. Run automatically with patch arg on commit."""

import sys
from configparser import ConfigParser


def bump_version():
    """Bumps version based on arg - major, minor, patch."""
    config = ConfigParser()
    config.read('settings.ini')

    version = config['SETTINGS']['version']

    major, minor, patch = map(int, version.split('.'))

    action = sys.argv[1]
    if action == 'major':
        major, minor, patch = major + 1, 0, 0
    elif action == 'minor':
        minor, patch = minor + 1, 0
    elif action == 'patch':
        patch = patch + 1

    version = f'{major}.{minor}.{patch}'

    config['SETTINGS']['version'] = version

    with open('settings.ini', 'w') as configfile:
        config.write(configfile)


if __name__ == '__main__':
    bump_version()
