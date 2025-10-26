#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$scriptDir/_common.ps1"

Ensure-Command 'pip-licenses'

$repoRoot = $env:REPO_ROOT
if (-not $repoRoot) {
    throw 'REPO_ROOT environment variable not set.'
}

$outputDir = Join-Path $repoRoot 'reports'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$rawReport = Join-Path $outputDir 'pip-licenses.json'

pip-licenses --from=auto --format=json --with-urls --output-file $rawReport

python (Join-Path $repoRoot 'scripts/_license_gate.py')
