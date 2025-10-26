#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

ruff format src tests scripts
black src tests scripts
isort src tests scripts
