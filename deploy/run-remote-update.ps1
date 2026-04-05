#Requires -Version 5.1
<#
.SYNOPSIS
  Windowsdan VPS: server-pull.sh + remote-update.sh (sizning SSH kalitingiz bilan).

  Cursor/agent muhitida server kaliti bo‘lmaydi — shuning uchun avtomatik SSH ishlamaydi.
  GitHub Actions (Secrets: DEPLOY_*) yoki ushbu skript ishlating.

.EXAMPLE
  $env:CLINICMON_DEPLOY_SSH_KEY = "$env:USERPROFILE\.ssh\clinicmonitoring_deploy"
  .\deploy\run-remote-update.ps1
#>
param(
    [string]$SshHost = "167.71.53.238",
    [string]$SshUser = "root"
)

$ErrorActionPreference = "Stop"

$keyPath = $env:CLINICMON_DEPLOY_SSH_KEY
if (-not $keyPath) {
    Write-Host "XATO: CLINICMON_DEPLOY_SSH_KEY muhit o'zgaruvchisida private kalit yo'lini ko'rsating." -ForegroundColor Yellow
    Write-Host '  Masalan: $env:CLINICMON_DEPLOY_SSH_KEY = "$env:USERPROFILE\.ssh\clinicmonitoring_deploy"' -ForegroundColor Gray
    exit 1
}
if (-not (Test-Path -LiteralPath $keyPath)) {
    Write-Error "Kalit fayli topilmadi: $keyPath"
    exit 1
}

$remoteCmd = "cd /opt/clinicmonitoring && bash deploy/server-pull.sh && bash deploy/remote-update.sh"
$sshArgs = @(
    "-i", $keyPath,
    "-o", "BatchMode=yes",
    "-o", "ConnectTimeout=20",
    "-o", "StrictHostKeyChecking=accept-new",
    "${SshUser}@${SshHost}",
    $remoteCmd
)

& ssh @sshArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
Write-Host "OK: deploy yakunlandi." -ForegroundColor Green
