#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

$report = $false
$filtered = @()
foreach ($arg in $Args) {
    if ($arg -eq '--report') {
        $report = $true
    } else {
        $filtered += $arg
    }
}
if ($filtered.Count -gt 0) {
    pytest --cov=red_teaming --cov-report=term-missing --cov-report=xml --cov-report=html $filtered
} else {
    pytest --cov=red_teaming --cov-report=term-missing --cov-report=xml --cov-report=html
}
if ($report) {
    Write-Host "HTML coverage report available in htmlcov/index.html"
}
