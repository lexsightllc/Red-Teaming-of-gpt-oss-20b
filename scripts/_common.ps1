$ErrorActionPreference = 'Stop'

$ScriptDir = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
$RepoRoot = Resolve-Path "$ScriptDir\.."
$Env:REPO_ROOT = $RepoRoot
$Env:PYTHONPATH = "$RepoRoot\src;$Env:PYTHONPATH"
$VenvPath = Join-Path $RepoRoot '.venv'
$ActivatePath = Join-Path $VenvPath 'Scripts\Activate.ps1'
if (Test-Path $ActivatePath) {
    . $ActivatePath
}

function Ensure-Command {
    param([string]$Name)
    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        Write-Error "Required command '$Name' not found. Run 'make bootstrap'."
    }
}
