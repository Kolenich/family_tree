#!/bin/sh

python bump_version.py patch
git update-index --add settings.ini