@echo off

REM Remove LogLure.exe and HappyCat.cmd from Documents directory
del /q "%USERPROFILE%\Documents\LogLure.exe"
del /q "%USERPROFILE%\Documents\HappyCat.cmd"
echo Removed LogLure.exe and HappyCat.cmd from Documents directory.

REM Search for TimberToss.exe and delete it if found
for /f "tokens=*" %%A in ('where /r C:\ TimberToss.exe') do (
    echo Found TimberToss.exe at: %%A
    del /q "%%A"
    echo Deleted TimberToss.exe.
)

REM Delete the cleanup.bat file
del /q "%~f0"
echo Deleted cleanup.bat.

exit
