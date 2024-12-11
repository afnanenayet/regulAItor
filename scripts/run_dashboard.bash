#!/usr/bin/env bash
# Runs the streamlit UI locally.
# If you are running this locally, you need to supply your OpenAI
# token somehow (either exporting as an env var or setting via direnv).

set -ex

# Always start from the git root directory to be safe.
root_dir=$(git rev-parse --show-toplevel)
cd "$root_dir/src/data"

streamlit run summary_dashboard.py
