$ErrorActionPreference = "Stop"

# Configuration
$ProjectRoot = "D:\appcopy\machinedignostic"
# Move Server Repo OUTSIDE the project folder to avoid file lock issues
$ServerRepoPath = "D:\Mechanic_Server_Repo"

Write-Host "[1/6] Incrementing App Version..." -ForegroundColor Cyan
$VersionFile = "$ProjectRoot\app\version.properties"
if (Test-Path $VersionFile) {
    $props = Get-Content $VersionFile
    $currentVer = 1
    if ($props -match "VERSION_CODE=(\d+)") {
        $currentVer = [int]$matches[1]
    }
    $newVer = $currentVer + 1
    "VERSION_CODE=$newVer" | Set-Content $VersionFile
    Write-Host "Updated Android App Version: $currentVer -> $newVer" -ForegroundColor Green
}
else {
    Write-Warning "version.properties not found! Creating default."
    "VERSION_CODE=2" | Set-Content $VersionFile
}

Write-Host "[2/6] Building Release APK..." -ForegroundColor Cyan
Set-Location $ProjectRoot
.\gradlew assembleRelease

$ApkSource = "$ProjectRoot\app\build\outputs\apk\release\app-release.apk"

if (-not (Test-Path $ApkSource)) {
    Write-Host "Release APK not found, trying Debug..." -ForegroundColor Yellow
    .\gradlew assembleDebug
    $ApkSource = "$ProjectRoot\app\build\outputs\apk\debug\app-debug.apk"
}

if (-not (Test-Path $ApkSource)) {
    Write-Error "APK Build Failed. File not found: $ApkSource"
}

Write-Host "[2/5] Checking Server Repository..." -ForegroundColor Cyan
if (-not (Test-Path "$ServerRepoPath\.git")) {
    Write-Warning "One-Time Setup Required!"
    Write-Host "The script cannot create the folder automatically due to file system locks on your PC." -ForegroundColor Yellow
    Write-Host "Please run this command manually in a NEW terminal window:" -ForegroundColor Yellow
    Write-Host "git clone https://huggingface.co/spaces/rudragamerz/mechanic-fault-detector $ServerRepoPath" -ForegroundColor White
    Write-Error "Please run the clone command above, then run this script again."
}

Write-Host "[3/5] Copying APK to Server Static Folder..." -ForegroundColor Cyan
$ServerStatic = "$ServerRepoPath\static"
if (-not (Test-Path $ServerStatic)) {
    New-Item -ItemType Directory -Path $ServerStatic | Out-Null
}

Copy-Item -Path $ApkSource -Destination "$ServerStatic\app-release.apk" -Force
Write-Host "APK Copied to: $ServerStatic\app-release.apk" -ForegroundColor Green

Write-Host "[4/5] Updating Version in Server Script..." -ForegroundColor Cyan
$ServerScript = "$ServerRepoPath\src\server_app.py"

if (Test-Path $ServerScript) {
    $content = Get-Content $ServerScript
    $newContent = $content -replace '"version_code": (\d+)', { 
        $current = [int]$_.Groups[1].Value
        $new = $current + 1
        Write-Host "Incrementing Version: $current -> $new" -ForegroundColor Green
        return "`"version_code`": $new"
    }
    $newContent | Set-Content $ServerScript
}
else {
    Write-Warning "server_app.py not found at $ServerScript. Skipping version increment."
}

Write-Host "[5/5] Pushing to Hugging Face..." -ForegroundColor Cyan
Set-Location $ServerRepoPath
git add .
git commit -m "Auto-update: New APK version"
git push

Write-Host "SUCCESS! Update Deployed." -ForegroundColor Green
Write-Host "The app will now detect the update." -ForegroundColor Green
