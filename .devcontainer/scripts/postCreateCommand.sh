#!/usr/bin/env bash

cecho() {
  RED="\033[0;31m"
  GREEN="\033[0;32m"  # <-- [0 means not bold
  YELLOW="\033[1;33m" # <-- [1 means bold
  CYAN="\033[1;36m"
  # ... Add more colors if you like

  NC="\033[0m" # No Color

  printf "${!1}${2} ${NC}\n" # <-- bash
}


cecho "CYAN" "Installing python packages (for local development)..."
python3 -m pip install -r requirements.txt --upgrade pip

echo "Adding aliases (for convenience)..."

# Build the container to test locally
echo "alias build=\"cd /workspaces/add-header-action && docker build -t add-header-action --no-cache .\"" >> ~/.zshrc

# Run the script locally
echo "alias run=\"cd /workspaces/add-header-action && python3 app/main.py\"" >> ~/.zshrc


cecho "GREEN" "-- Init complete -- Nautical development enviornment ready to go!!"


zsh && omz reload
# No need to 'source ~/.zshrc' since the terminal won't be open yet
