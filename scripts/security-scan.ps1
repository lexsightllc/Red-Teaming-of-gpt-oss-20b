#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

bandit -q -r src
pip-audit -r requirements/base.txt -r requirements/dev.txt $Args
