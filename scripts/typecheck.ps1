#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/_common.ps1"

mypy src tests
