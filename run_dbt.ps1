## Repo-root shortcut for dbt — delegates to src/run_dbt.ps1
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DbtArgs
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& (Join-Path $scriptDir "src\run_dbt.ps1") @DbtArgs
exit $LASTEXITCODE
