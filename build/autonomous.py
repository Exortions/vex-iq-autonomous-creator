import drivetrain as dt
import vexiq
import sys

drivetrain = dt.Drivetrain(vexiq.Motor(1, False), vexiq.Motor(6, True), 200, 176)


drivetrain.drive_until(100, 210)
drivetrain.turn_until(100, -69)

