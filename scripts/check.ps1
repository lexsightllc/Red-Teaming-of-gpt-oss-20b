#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

& "$RepoRoot/scripts/lint.ps1" $Args
& "$RepoRoot/scripts/typecheck.ps1"
& "$RepoRoot/scripts/test.ps1"
& "$RepoRoot/scripts/e2e.ps1"
& "$RepoRoot/scripts/coverage.ps1"
& "$RepoRoot/scripts/security-scan.ps1"
