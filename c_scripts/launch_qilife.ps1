Start-Process powershell -Verb runAs -ArgumentList @"
cd 'C:\Users\codyr\Documents\GitHub\qilife'
python c_scripts\run_dev.py
Write-Host '⏹ Press Enter to exit...' -ForegroundColor Yellow
Read-Host
"@
