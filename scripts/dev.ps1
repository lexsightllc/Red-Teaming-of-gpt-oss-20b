#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

Ensure-Command python
try {
    python -m watchfiles --help | Out-Null
    python -m watchfiles --filter python -- python -m red_teaming.cli $Args
} catch {
    python -m red_teaming.cli $Args
}
