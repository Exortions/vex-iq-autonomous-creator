@echo off

echo Compiling build.exe
pyinstaller --onefile .\.compiledsource\build.py

echo Compiling compile.exe
pyinstaller --onefile .\.compiledsource\compile.py

echo Cleaning up

del .\build\build /F /Q
del .\build\compile /F /Q

del .\build.spec /F /Q
del .\compile.spec /F /Q

move .\dist\build.exe .
move .\dist\compile.exe .

del .\dist /F /Q

echo Cleanup complete

echo Done

pause
