@echo off
echo Killing Java and ADB processes...
taskkill /F /IM java.exe
taskkill /F /IM adb.exe
echo Processes killed.

echo Deleting old build directories...
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v9
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v8
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v7
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v6
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v5
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v4
rmdir /S /Q d:\appcopy\machinedignostic\app\build_final_v3
rmdir /S /Q d:\appcopy\machinedignostic\app\build_safe_revert
echo Old build directories deleted.

echo Ready for clean build in build_final_v8.
pause
