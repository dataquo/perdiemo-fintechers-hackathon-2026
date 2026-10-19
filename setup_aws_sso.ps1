# ==============================================================================
# setup_aws_sso.ps1 — Interactive AWS SSO Setup Helper for Hackathon Team
# ==============================================================================
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  AWS Hackathon SSO Configuration — Quick Reference Guide  " -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "When 'aws configure sso' prompts you, answer as follows:" -ForegroundColor Yellow
Write-Host "  1. SSO session name:           hackathon" -ForegroundColor Green
Write-Host "  2. SSO start URL:              https://d-c3676ff6eb.awsapps.com/start" -ForegroundColor Green
Write-Host "  3. SSO region:                 eu-north-1  <-- Stockholm (Sign-in directory)" -ForegroundColor Magenta
Write-Host "  4. SSO registration scopes:    [press Enter to accept default]" -ForegroundColor Green
Write-Host "  --> [Browser will open to log in with Email, OTP & Phone Authenticator] <--" -ForegroundColor White
Write-Host "  5. Select Account:             [Choose your Team Account]" -ForegroundColor Green
Write-Host "  6. Select Role:                ai-hackathon-TeamAdmin" -ForegroundColor Green
Write-Host "  7. CLI default client region:  eu-central-1  <-- Frankfurt (Where you build)" -ForegroundColor Magenta
Write-Host "  8. CLI default output format:  json" -ForegroundColor Green
Write-Host "  9. CLI profile name:           hackathon" -ForegroundColor Green
Write-Host ""
Write-Host "Launching 'aws configure sso' now..." -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan

# Ensure AWS CLI is in PATH for this session
if ($env:PATH -notlike "*C:\Program Files\Amazon\AWSCLIV2*") {
    $env:PATH = "C:\Program Files\Amazon\AWSCLIV2;" + $env:PATH
}

aws configure sso
