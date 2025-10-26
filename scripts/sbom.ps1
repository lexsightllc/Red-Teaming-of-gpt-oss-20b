#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

New-Item -ItemType Directory -Force -Path "$RepoRoot/sbom" | Out-Null
cyclonedx-bom -e -o "$RepoRoot/sbom/sbom.json"
