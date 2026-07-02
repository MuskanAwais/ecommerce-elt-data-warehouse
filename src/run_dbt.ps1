## PowerShell helper to run dbt with project-local profiles.
## Works from ANY directory — always invoke via full path from repo root:
##   .\src\run_dbt.ps1 test
## Or use the repo-root shortcut:
##   .\run_dbt.ps1 test

param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DbtArgs
)

$ErrorActionPreference = "Stop"

$srcRoot = $PSScriptRoot
$repoRoot = Split-Path -Parent $srcRoot
$profilesDir = Join-Path $repoRoot "config"
$dbtProjectDir = Join-Path $srcRoot "transformations"
$venvDbt = Join-Path $repoRoot ".venv\Scripts\dbt.exe"

if (-not (Test-Path $dbtProjectDir)) {
    Write-Error "dbt project not found at: $dbtProjectDir"
}

# Prefer venv dbt so users don't need a global install
if (Test-Path $venvDbt) {
    $dbtCmd = $venvDbt
} else {
    $dbtCmd = (Get-Command dbt -ErrorAction SilentlyContinue).Source
    if (-not $dbtCmd) {
        Write-Error @"
dbt not found. Activate the virtual environment and install dependencies:
  .\.venv\Scripts\Activate.ps1
  pip install -r requirements.txt
"@
    }
}

$env:DBT_PROFILES_DIR = $profilesDir
$previousLocation = Get-Location

try {
    Set-Location $dbtProjectDir
    Write-Host "Running: dbt $($DbtArgs -join ' ')  (project: $dbtProjectDir)" -ForegroundColor Cyan
    & $dbtCmd @DbtArgs
    exit $LASTEXITCODE
}
finally {
    Set-Location $previousLocation
}
