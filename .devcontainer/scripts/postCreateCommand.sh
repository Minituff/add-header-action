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
python3 -m pip install -r requirements-dev.txt --upgrade pip

echo "Adding aliases (for convenience)..."
for file in ~/.zshrc ~/.bashrc; do
  # Go back to the workspace directory
  echo "alias home=\"cd /workspaces/add-header-action\"" >> "$file"

  echo "alias cls=\"clear\"" >> "$file"

  # Build the container to test locally
  echo "alias build=\" home && cls && docker build -t minituff/add-header-action --no-cache .\"" >> "$file"

  # Run the script locally
  echo "alias run=\"home && cls && python3 app/main.py --verbose false --dry-run false\"" >> "$file"

  # Format all python files in /app and /test
  echo "alias format=\"python3 -m black --line-length 120 app test\"" >> "$file"

  # Run pytest and output report as hmtl
  echo "alias test=\"home && cls && python3 -m pytest -vs --cov app --cov-report html --cov-report term\"" >> "$file"
done


cecho "CYAN" "Installing pre-commit..."
pre-commit install


cecho "GREEN" "-- Init complete -- Development enviornment ready to go!!"


zsh && omz reload
# No need to 'source ~/.zshrc' since the terminal won't be open yet
