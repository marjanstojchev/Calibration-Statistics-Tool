Set-Location "C:\Calibration Statistics Tool"
git add -f tests/e2e/*.py
git status
git commit -m "fix: add E2E test files to git (force)"
git push origin web-cloud-ui
Write-Host "DONE"
