@echo off

build.exe
echo Copy the file build/creator.py to your robot
echo Run the program, and place the output in config/input.json
pause
compile.exe
echo Finished! Run the build/autonomous.py on your robot.
