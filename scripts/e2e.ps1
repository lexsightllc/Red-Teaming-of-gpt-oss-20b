#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

pytest tests/e2e $Args
