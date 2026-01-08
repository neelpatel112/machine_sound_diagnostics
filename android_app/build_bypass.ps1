Write-Host "Stopping Gradle Daemon..."
cmd /c "gradlew --stop"

Write-Host "Killing potentially locking processes..."
Stop-Process -Name "java" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "adb" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "kotlin-daemon" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "studio64" -ErrorAction SilentlyContinue -Force 

Start-Sleep -Seconds 2

Write-Host "Starting Build..."
cmd /c "gradlew assembleDebug --no-daemon"
