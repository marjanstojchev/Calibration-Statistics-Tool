@echo off
cd /d "C:\Calibration Statistics Tool"
git add .gitlab-ci.yml
git commit -m "feat(ci): Add dedicated E2E test stage with full stack environment"
git push origin web-cloud-ui
git push github web-cloud-ui
echo Done!
pause
