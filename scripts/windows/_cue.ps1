# =============================================================================
# _cue.ps1 - Shared Cue command logic
# Not meant to be run directly. Called by the .bat scripts.
# =============================================================================

param(
    [Parameter(Mandatory)][string]$Command
)

. "$PSScriptRoot\config.ps1"

function Send-CueCommand($display, $command) {
    $url  = "http://$($display.host):$($display.port)/command"
    $body = @{ command = $command } | ConvertTo-Json
    try {
        Invoke-RestMethod `
            -Uri         $url `
            -Method      POST `
            -Body        $body `
            -ContentType "application/json" `
            -Headers     @{ "X-API-Key" = $display.api_key } `
            -TimeoutSec  5 | Out-Null
        Write-Host "  [OK] $($display.name)" -ForegroundColor Green
    } catch {
        Write-Host "  [FAIL] $($display.name): $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Sending '$Command' to all displays..." -ForegroundColor Cyan
Write-Host ""

foreach ($d in $displays) {
    Send-CueCommand $d $Command
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
