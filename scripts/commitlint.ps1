#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

param([string]$MessageFile)
if (-not $MessageFile -or -not (Test-Path $MessageFile)) {
    Write-Error "Usage: scripts/commitlint.ps1 <commit-msg-file>"
}

$pattern = '^(build|chore|ci|docs|feat|fix|perf|refactor|revert|style|test)(\([a-z0-9-]+\))?(\!)?: [^\s].+'
$message = (Get-Content -Path $MessageFile -Raw).Trim()
if (-not $message) {
    exit 0
}
if (-not ($message -match $pattern)) {
    Write-Error "Commit message must follow Conventional Commits (e.g. 'feat(control): add guard')."
}
if ($message.Length -gt 100) {
    Write-Error "Commit message subject should be 100 characters or fewer."
}
