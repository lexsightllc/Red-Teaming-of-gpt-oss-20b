#!/usr/bin/env pwsh
. "$PSScriptRoot/_common.ps1"

$paths = @('build','dist','htmlcov','.coverage','coverage.xml','.mypy_cache','.pytest_cache','mkdocs-site','site')
foreach ($path in $paths) {
    $full = Join-Path $RepoRoot $path
    if (Test-Path $full) {
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $full
    }
}
$sbomDir = Join-Path $RepoRoot 'sbom'
if (Test-Path $sbomDir) {
    Get-ChildItem -Path $sbomDir -Filter '*.json' | Remove-Item -Force -ErrorAction SilentlyContinue
}
Get-ChildItem -Path (Join-Path $RepoRoot 'src'), (Join-Path $RepoRoot 'tests') -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force
