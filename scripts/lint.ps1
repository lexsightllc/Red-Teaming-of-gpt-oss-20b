#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

$targets = @('src', 'tests', 'scripts')
if ($Args -contains '--fix') {
    ruff check --fix
    black $targets
    isort $targets
} else {
    ruff check
    black --check $targets
    isort --check-only $targets
}
