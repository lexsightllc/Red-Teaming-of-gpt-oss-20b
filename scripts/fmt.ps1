#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/_common.ps1"

ruff format src tests scripts
black src tests scripts
isort src tests scripts
