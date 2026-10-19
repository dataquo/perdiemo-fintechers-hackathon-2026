# ==============================================================================
# aws_login.ps1 — 1-Click AWS SSO Login & Identity Verification
# ==============================================================================
Write-Host "Logging into AWS Hackathon SSO (Profile: martin-hackathon)..." -ForegroundColor Cyan

if ($env:PATH -notlike "*C:\Program Files\Amazon\AWSCLIV2*") {
    $env:PATH = "C:\Program Files\Amazon\AWSCLIV2;" + $env:PATH
}

aws sso login --profile martin-hackathon

Write-Host "`nVerifying active identity..." -ForegroundColor Yellow
aws sts get-caller-identity --profile martin-hackathon
