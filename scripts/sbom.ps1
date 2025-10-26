#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/_common.ps1"

New-Item -ItemType Directory -Force -Path "$RepoRoot/sbom" | Out-Null
cyclonedx-bom -e -o "$RepoRoot/sbom/sbom.json"
