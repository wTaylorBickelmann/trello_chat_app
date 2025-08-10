#!/usr/bin/env bash

# fail fast
set -euo pipefail

ENV_NAME="trello_llm"

# Make sure conda is initialised for non-interactive shells
source "$(conda info --base)/etc/profile.d/conda.sh"

if ! conda env list | grep -qE "^${ENV_NAME}[[:space:]]"; then
  echo "Creating conda environment '$ENV_NAME' from environment.yml …"
  conda env create -f environment.yml
else
  echo "Conda environment '$ENV_NAME' already exists."
  read -p "Update the environment with environment.yml? [y/N] " -r REPLY
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Updating environment …"
    conda env update -n "$ENV_NAME" -f environment.yml
  else
    echo "Skipping update."
  fi
fi

# Activate the env for the remainder of the script
conda activate "$ENV_NAME"

echo "Environment '$ENV_NAME' is active."

# Load .env variables into the current shell session, if the file exists
if [[ -f .env ]]; then
  echo "Loading variables from .env …"
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs) || true
fi

echo "Done."
