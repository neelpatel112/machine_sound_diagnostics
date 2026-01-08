@echo off
echo Setting up Server Repository in D:\Mechanic_Server_Repo...

:: 1. Cleanup existing folder if it's broken
if exist "D:\Mechanic_Server_Repo" (
    echo Removing existing folder to start fresh...
    rmdir /s /q "D:\Mechanic_Server_Repo"
)

:: 2. Clone the repository
echo Cloning from Hugging Face...
git clone https://huggingface.co/spaces/rudragamerz/mechanic-fault-detector D:\Mechanic_Server_Repo

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Git Clone Failed! 
    echo Please make sure you have Git installed and an internet connection.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Repository Cloned Successfully!
echo You can now run .\deploy_update.ps1
pause
