$gradleFile = "d:\appcopy\machinedignostic\app\build.gradle.kts"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$newBuildDir = "C:/Users/Lenovo/.gemini/antigravity/tmp_builds/machinedignostic_$timestamp"

Write-Host "Rotated Build Directory Strategy"
Write-Host "Killing processes..."
Stop-Process -Name "java" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "adb" -ErrorAction SilentlyContinue -Force
Stop-Process -Name "kotlin-daemon" -ErrorAction SilentlyContinue -Force

Write-Host "Updating build.gradle.kts to use $newBuildDir..."
$content = Get-Content $gradleFile -Raw
# Regex to find the layout.buildDirectory line and replace it
$newContent = $content -replace 'layout\.buildDirectory\.set\(file\(".*?"\)\)', "layout.buildDirectory.set(file(`"$newBuildDir`"))"

if ($newContent -eq $content) {
    # If regex didn't match (maybe commented out or different format), append/insert it or warn
    # Try simpler match or just force it if we know the structure. 
    # Based on previous reads, we know the line exists.
    Write-Warning "Regex replace failed. Attempting fallback replacement."
    $newContent = $content -replace 'layout\.buildDirectory\.set\(file\(".*?"\)\)', "layout.buildDirectory.set(file(`"$newBuildDir`"))"
}

Set-Content -Path $gradleFile -Value $newContent

Write-Host "Starting Build in $newBuildDir..."
cmd /c "gradlew assembleDebug --no-daemon"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Build Successful! APK is in $newBuildDir/outputs/apk/debug/app-debug.apk"
    # Optional: Copy APK to a consistent location?
    # copy app/$newBuildDir/outputs/apk/debug/app-debug.apk app/app-debug.apk
} else {
    Write-Host "Build Failed."
}
