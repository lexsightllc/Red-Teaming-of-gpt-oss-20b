#!/usr/bin/env pwsh
# SPDX-License-Identifier: MPL-2.0

. "$PSScriptRoot/_common.ps1"

pip-compile --resolver=backtracking --upgrade --output-file requirements/base.txt requirements/base.in
pip-compile --resolver=backtracking --upgrade --output-file requirements/dev.txt requirements/dev.in
