Write-Host "Stopping Gradle Daemon..."
cmd /c "gradlew --stop"

Write-Host "Killing potentially locking processes..."
Stop-Process -Name "java" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "adb" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "kotlin-daemon" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "studio64" -ErrorAction SilentlyContinue -Force 

Start-Sleep -Seconds 2

$dirs = @(
    "d:\appcopy\machinedignostic\app\build",
    "d:\appcopy\machinedignostic\app\build_final_v10",
    "d:\appcopy\machinedignostic\app\build_final_v9",
    "d:\appcopy\machinedignostic\.gradle"
)

foreach ($d in $dirs) {
    if (Test-Path $d) {
        Write-Host "Attempting to remove $d..."
        Remove-Item -Recurse -Force $d -ErrorAction SilentlyContinue
        
        if (Test-Path $d) {
             Write-Host "Deletion failed. Attempting to rename $d to ${d}_TRASH..."
             $trashName = "${d}_TRASH_" + (Get-Date -Format "yyyyMMddHHmmss")
             Rename-Item -Path $d -NewName $trashName -ErrorAction SilentlyContinue
             
             if (Test-Path $d) {
                 Write-Host "ERROR: Could not delete OR rename $d. Manual intervention might be required."
             } else {
                 Write-Host "Renamed locked folder to $trashName. Proceeding."
             }
        }
    }
}

Write-Host "Starting Clean Build..."
cmd /c "gradlew clean assembleDebug --no-daemon"
