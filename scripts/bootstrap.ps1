#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

python -m venv "$RepoRoot/.venv"
& "$RepoRoot/.venv/Scripts/Activate.ps1"
python -m pip install --upgrade pip
python -m pip install -r "$RepoRoot/requirements/base.txt" -r "$RepoRoot/requirements/dev.txt"
pre-commit install --hook-type pre-commit --hook-type commit-msg
& git config commit.template "$RepoRoot/.gitmessage"
Write-Host "Bootstrap complete. Run 'make check' to validate the environment."
