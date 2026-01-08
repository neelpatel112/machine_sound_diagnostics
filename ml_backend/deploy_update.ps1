<#
.SYNOPSIS
    Automates the Android APK Build and Server Deployment process.
.DESCRIPTION
    1. Builds the Android APK (Release mode) using Gradle.
    2. Copies the APK to the Python Server's 'static' folder.
    3. Updates the version code in server_app.py automatically.
    4. Commits and Pushes changes to Hugging Face.
#>

# CONFIGURATION
$AndroidProjectPath = "D:\appcopy\machinedignostic"  # <--- VERIFY THIS PATH
$ServerRepoPath = "D:\COPY\finalminorproject"        # <--- VERIFY THIS PATH
$HuggingFaceRemote = "https://huggingface.co/spaces/RudraGamerz/mechanic-fault-detector"

Write-Host "🚀 Starting Auto-Deployment..." -ForegroundColor Cyan

# 1. BUILD APK
Write-Host "Step 1: Building APK..." -ForegroundColor Yellow
Set-Location $AndroidProjectPath
# Use cmd /c to run gradlew bat file
cmd /c "gradlew.bat assembleRelease"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build Failed! Check Android Studio errors."
    exit
}

# 2. LOCATE APK
$ApkSource = "$AndroidProjectPath\app\build\outputs\apk\release\app-release.apk"
# Fallback to debug if release not signed/configured
if (-not (Test-Path $ApkSource)) {
    Write-Warning "Release APK not found. Checking for Debug APK..."
    $ApkSource = "$AndroidProjectPath\app\build\outputs\apk\debug\app-debug.apk"
}

if (-not (Test-Path $ApkSource)) {
    Write-Error "APK file not found at: $ApkSource"
    exit
}

# 3. COPY TO SERVER
Write-Host "Step 2: Copying to Server..." -ForegroundColor Yellow
$DestDir = "$ServerRepoPath\static"
if (-not (Test-Path $DestDir)) { New-Item -ItemType Directory -Path $DestDir | Out-Null }
Copy-Item -Path $ApkSource -Destination "$DestDir\app-release.apk" -Force

# 4. UPDATE VERSION IN PYTHON
Write-Host "Step 3: Incrementing Version Code..." -ForegroundColor Yellow
$ServerFile = "$ServerRepoPath\src\server_app.py"
$Content = Get-Content $ServerFile -Raw

# Regex to find "version_code": 123
if ($Content -match '"version_code":\s*(\d+)') {
    $CurrentVersion = [int]$matches[1]
    $NewVersion = $CurrentVersion + 1
    $Content = $Content -replace '"version_code":\s*\d+', """version_code"": $NewVersion"
    Set-Content -Path $ServerFile -Value $Content
    Write-Host "Updated Version: $CurrentVersion -> $NewVersion" -ForegroundColor Green
} else {
    Write-Warning "Could not find version_code in server_app.py"
}

# 5. GIT PUSH
Write-Host "Step 4: Pushing to Hugging Face..." -ForegroundColor Yellow
Set-Location $ServerRepoPath

# Check if git is initialized
if (-not (Test-Path ".git")) {
    git init
    git remote add origin $HuggingFaceRemote
}

git add .
git commit -m "Auto-deploy: Version $NewVersion"
git push origin main

Write-Host "✅ Deployment Complete!" -ForegroundColor Green
Write-Host "The app will update automatically."
