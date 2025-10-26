#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

pip-compile --resolver=backtracking --upgrade --output-file requirements/base.txt requirements/base.in
pip-compile --resolver=backtracking --upgrade --output-file requirements/dev.txt requirements/dev.in
