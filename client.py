import drivetrain
import asyncio
import vexiq
import sys

configuration = {
    'default_power': 100,
    'motors': {
        'drivetrain': {
            'left': {
                'port': 6,
                'reverse_polarity': False
            },
            'right': {
                'port': 12,
                'reverse_polarity': True
            },
        },
        'other': {
            'catapult': {
                'type': 'dual',
                'motors': [
                    {
                        'port': 1,
                        'reverse_polarity': False
                    },
                    {
                        'port': 2,
                        'reverse_polarity': True
                    }
                ]
            }
        }
    },
    'always_run': [
        {
            'port': 5,
            'reverse_polarity': False,
            'power': 100
        }
    ]
}

DEFAULT_POWER = configuration['default_power']

ACTION_TYPES = ['always_run', 'move', 'sleep', 'turn', 'run_motor']


def convertAlwaysRunActionToCode(action):
    return 'vexiq.Motor(' + action["port"] + ', ' + action["reverse_polarity"] + ').run_until(' + action["value"] + ')'


def convertMoveActionToCode(action):
    return 'dt.drive_until(' + DEFAULT_POWER + ', ' + action['value'] + ')'


def convertSleepActionToCode(action):
    return 'sys.sleep(' + action['value'] + ')'


def convertTurnActionToCode(action):
    return 'dt.turn_until(' + DEFAULT_POWER + ', ' + action['value'] + ')'


def convertMotorToCode(motor, value):
    return 'vexiq.Motor(' + motor["port"] + ', ' + motor["reverse_polarity"] + ').run_until(' + DEFAULT_POWER + ', ' + value + ')'


def convertMotorRunToCode(action):
    code = ''

    isDual = action['isDual']
    motors = action['motors']
    value = action['value']

    if isDual:
        motor_one = motors[0]
        motor_two = motors[1]

        code += convertMotorToCode(motor=motor_one, value=value)
        code += '\n'
        code += convertMotorToCode(motor=motor_two, value=value)
    else:
        motor = motors[0]

        code += convertMotorToCode(motor=motor, value=value)

    return code


def convertCode(actions, config):
    code = ''

    drivetrain = config['motors']['drivetrain']

    left_motor = 'vexiq.Motor(' + drivetrain["left"]["port"] + \
        ', ' + drivetrain["left"]["reverse_polarity"] + ')'
    right_motor = 'vexiq.Motor(' + drivetrain["right"]["port"] + \
        ', ' + drivetrain["right"]["reverse_polarity"] + ')'

    code += 'import drivetrain\nimport vexiq\nimport sys\n\ndt = drivetrain.Drivetrain(' + \
        left_motor + ', ' + right_motor + ', 200, 176)\n\n'

    for action in actions:
        actionType = action['type']

        if actionType == None or actionType not in ACTION_TYPES:
            continue

        if actionType == 'always_run':
            code += convertAlwaysRunActionToCode(action=action)
        elif actionType == 'move':
            code += convertMoveActionToCode(action=action)
        elif actionType == 'sleep':
            code += convertSleepActionToCode(action=action)
        elif actionType == 'turn':
            code += convertTurnActionToCode(action=action)
        elif actionType == 'run_motor':
            code += convertMotorRunToCode(action=action)
        else:
            continue

        code += '\n'

    return code


actions = []

joystick = vexiq.Joystick()


def log(message, row=1, column=1):
    vexiq.lcd_write(message, row, column)


def update(value):
    log('Select a value')
    log('Current >> ' + value, 2, 1)


def actionSelection(_callback=None):
    typesOfActions = ['Move', 'Wait', 'Turn', 'Run Motor']

    CURRENT_ACTION = typesOfActions[1]

    while True:
        if left():
            CURRENT_ACTION = typesOfActions[(typesOfActions.index(
                CURRENT_ACTION) - 1) % len(typesOfActions)]
            update(CURRENT_ACTION)
        elif right():
            CURRENT_ACTION = typesOfActions[(typesOfActions.index(
                CURRENT_ACTION) + 1) % len(typesOfActions)]
            update(CURRENT_ACTION)
        elif select():
            if _callback != None:
                _callback(CURRENT_ACTION)

            return CURRENT_ACTION

        sys.sleep(0.01)


def portSelection(_callback=None):
    CURRENT_PORT = 0

    while True:
        if left():
            if CURRENT_PORT <= 0:
                CURRENT_PORT = 0
            else:
                CURRENT_PORT -= 1
            update(CURRENT_PORT)
        elif right():
            if CURRENT_PORT >= 12:
                CURRENT_PORT = 12
            else:
                CURRENT_PORT += 1
            update(CURRENT_PORT)
        elif select():
            if _callback != None:
                _callback(CURRENT_PORT)

            return CURRENT_PORT

        sys.sleep(0.01)


def drivetrainValueSelection(_callback=None):
    CURRENT_VALUE = 0

    while True:
        if left():
            CURRENT_VALUE -= 1
            update(CURRENT_VALUE)
            dt.drive(DEFAULT_POWER, -1)
        elif right():
            CURRENT_VALUE += 1
            update(CURRENT_VALUE)
            dt.drive(DEFAULT_POWER, 1)
        elif select():
            if _callback != None:
                _callback(CURRENT_VALUE)

            return CURRENT_VALUE

        sys.sleep(0.01)


def waitValueSelection(_callback=None):
    CURRENT_VALUE = 0

    while True:
        if left():
            CURRENT_VALUE -= 1
            update(CURRENT_VALUE)
        elif right():
            CURRENT_VALUE += 1
            update(CURRENT_VALUE)
        elif select():
            if _callback != None:
                _callback(CURRENT_VALUE)

            return CURRENT_VALUE

        sys.sleep(0.01)


def turnValueSelection(_callback=None):
    CURRENT_VALUE = 0

    while True:
        if left():
            CURRENT_VALUE -= 1
            update(CURRENT_VALUE)

            dt.turn_until(DEFAULT_POWER, -1)
        elif right():
            CURRENT_VALUE += 1
            update(CURRENT_VALUE)

            dt.turn_until(DEFAULT_POWER, 1)
        elif select():
            if _callback != None:
                _callback(CURRENT_VALUE)

            return CURRENT_VALUE

        sys.sleep(0.01)


def motorNameSelection(_callback=None):
    motors = configuration['motors']['other'].keys()

    CURRENT_MOTOR = motors[0]

    while True:
        if left():
            CURRENT_MOTOR = motors[(motors.index(
                CURRENT_MOTOR) - 1) % len(motors)]
            update(CURRENT_MOTOR)
        elif right():
            CURRENT_MOTOR = motors[(motors.index(
                CURRENT_MOTOR) + 1) % len(motors)]
            update(CURRENT_MOTOR)
        elif select():
            if _callback != None:
                _callback(CURRENT_MOTOR)

            return CURRENT_MOTOR

        sys.sleep(0.01)


def motorValueSelection(name, _callback=None):
    motor = configuration['motors']['other'][name]

    isDual = True if motor['type'] == 'dual' else False

    CURRENT_VALUE = 0

    while True:
        if isDual:
            motorOne = vexiq.Motor(
                motor['motors'][0]['port'], motor['motors'][0]['reverse_polarity'])
            motorTwo = vexiq.Motor(
                motor['motors'][1]['port'], motor['motors'][1]['reverse_polarity'])

            if left():
                CURRENT_VALUE -= 1
                update(CURRENT_VALUE)

                motorOne.run_until(DEFAULT_POWER, -1)
                motorTwo.run_until(DEFAULT_POWER, -1)
            elif right():
                CURRENT_VALUE += 1
                update(CURRENT_VALUE)

                motorOne.run_until(DEFAULT_POWER, 1)
                motorTwo.run_until(DEFAULT_POWER, 1)
            elif select():
                if _callback != None:
                    _callback(CURRENT_VALUE, name)

                return CURRENT_VALUE
        else:
            motorOne = vexiq.Motor(
                motor['motors'][0]['port'], motor['motors'][0]['reverse_polarity'])

            if left():
                CURRENT_VALUE -= 1
                update(CURRENT_VALUE)

                motorOne.run_until(DEFAULT_POWER, -1)
            elif right():
                CURRENT_VALUE += 1
                update(CURRENT_VALUE)

                motorOne.run_until(DEFAULT_POWER, 1)
            elif select():
                if _callback != None:
                    _callback(CURRENT_VALUE, name)

                return CURRENT_VALUE


def drivetrainValueSelectionCallback(value):
    action = {
        'type': 'move',
                'value': int(value)
    }

    actions.append(action)


def waitValueSelectionCallback(value):
    action = {
        'type': 'wait',
        'value': int(value)
    }

    actions.append(action)


def turnValueSelectionCallback(value):
    action = {
        'type': 'turn',
        'value': int(value)
    }

    actions.append(action)


def motorValueSelectionCallback(value, name):
    action = {
        'type': 'run_motor',
        'name': name,
        'isDual': True if configuration['motors']['other'][name]['type'] == 'dual' else False,
        'motors': configuration['motors']['other'][name]['motors'],
        'value': int(value)
    }

    actions.append(action)


def motorNameSelectionCallback(name):
    motorValueSelection(name, motorValueSelectionCallback)


def actionSelectCallback(actionType):
    if actionType == 'Move':
        drivetrainValueSelection(drivetrainValueSelectionCallback)
    elif actionType == 'Wait':
        waitValueSelection(waitValueSelectionCallback)
    elif actionType == 'Turn':
        turnValueSelection(turnValueSelectionCallback)
    elif actionType == 'run_motor':
        motorNameSelection(motorNameSelectionCallback)


def main():
    left = joystick.bLup
    select = joystick.bRdown
    right = joystick.bRup

    SELECTION_STATE = 'ACTION_SELECTION'

    dtConfig = configuration['motors']['drivetrain']

    leftDT = vexiq.Motor(dtConfig['left']['port'],
                         dtConfig['left']['reverse_polarity'])
    rightDT = vexiq.Motor(
        dtConfig['right']['port'], dtConfig['right']['reverse_polarity'])

    dt = drivetrain.Drivetrain(leftDT, rightDT, 200, 176)

    actionType = actionSelection()


def run():
    for alwaysRun in configuration['always_run']:
        action = {
            'type': 'always_run',
            'port': alwaysRun['port'],
            'reverse_polarity': alwaysRun['reverse_polarity'],
            'value': alwaysRun['value']
        }

    while True:
        if joystick.bLdown():
            code = convertCode(actions=actions, config=configuration)

            print(code)

            exit(-1)

            break

        main()


if __name__ == '__main__':
    print('Starting autonomous creator...')
    print('Press LD to generate code and exit')
    print('\n----------------------------------\n')
    run()
    print('----------------------------------\n')
