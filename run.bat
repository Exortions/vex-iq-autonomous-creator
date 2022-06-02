@echo off

build.exe
python minify.py build/creator.py
echo Copy the file build/creator.py to your robot
echo Run the program, and place the output in config/input.json
pause
compile.exe
python minify.py build/autonomous.py
echo Finished! Run the build/autonomous.py on your robot.
