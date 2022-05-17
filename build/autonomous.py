import drivetrain as dt
import vexiq
import sys

drivetrain = dt.Drivetrain(vexiq.Motor(1, False), vexiq.Motor(6, True), 200, 176)


drivetrain.drive_until(100, 50)
drivetrain.turn_until(100, 90)
sys.sleep(0.2)
while True:
    vexiq.lcd_write("Auton finisheed")
    sys.sleep(1)
    sys.exit()
