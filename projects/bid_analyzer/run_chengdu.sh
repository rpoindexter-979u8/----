#!/usr/bin/env zsh
set -e

# Ensure user-level Python scripts (including streamlit) are in PATH.
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

python3 -m streamlit run dynamic_app_chengdu_museum.py
