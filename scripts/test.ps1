#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

pytest tests/unit tests/integration $Args
