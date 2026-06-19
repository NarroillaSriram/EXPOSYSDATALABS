@echo off
echo Starting Exposys Data Labs Services...

:: Start Express Backend on port 5001
echo Starting Blockchain Express Backend...
start cmd /k "cd certificate_system\backend && node server.js"

:: Start React Frontend on port 5173
echo Starting Blockchain React Frontend...
start cmd /k "cd certificate_system\frontend && npm run dev"

:: Start Flask App on port 5000
echo Starting Flask App...
venv\Scripts\python.exe app.py

pause
