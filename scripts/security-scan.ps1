#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$scriptDir/_common.ps1"

bandit -q -r src
pip-audit -r requirements/base.txt -r requirements/dev.txt @args
& "$env:REPO_ROOT/scripts/license-scan.ps1"
pre-commit run detect-private-key --all-files
