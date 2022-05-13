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


def convertAlwaysRunActionToCode(action) -> str:
    return f'vexiq.Motor({action["port"]}, {action["reverse_polarity"]}).run_until({action["value"]})'


def convertMoveActionToCode(action) -> str:
    return f'dt.drive_until({DEFAULT_POWER}, {action["value"]})'


def convertSleepActionToCode(action) -> str:
    return f'sys.sleep({action["value"]})'


def convertTurnActionToCode(action) -> str:
    return f'dt.turn_until({DEFAULT_POWER}, {action["value"]})'


def convertMotorToCode(motor, value) -> str:
    return f'vexiq.Motor({motor["port"]}, {motor["reverse_polarity"]}).run_until({DEFAULT_POWER}, {value})'


def convertMotorRunToCode(action) -> str:
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


def convertCode(actions, config) -> str:
    code = ''

    drivetrain = config['motors']['drivetrain']

    left_motor = f'vexiq.Motor({drivetrain["left"]["port"]}, {drivetrain["left"]["reverse_polarity"]})'
    right_motor = f'vexiq.Motor({drivetrain["right"]["port"]}, {drivetrain["right"]["reverse_polarity"]})'

    code += f'import drivetrain\nimport vexiq\nimport sys\n\ndt = drivetrain.Drivetrain({left_motor}, {right_motor}, 200, 176)\n\n'

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


async def main():

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

    async def actionSelection():
        typesOfActions = ['Move', 'Wait', 'Turn', 'Run Motor']

        CURRENT_ACTION = typesOfActions[1]

        def update(action):
            log('Select an action')
            log(f'Current >> {CURRENT_ACTION}', 2, 1)

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
                return CURRENT_ACTION

            sys.sleep(0.01)

    async def portSelection():
        CURRENT_PORT = 0

        def update(port):
            log('Select a port')
            log(f'Current >> {port}', 2, 1)

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
                return CURRENT_PORT

            sys.sleep(0.01)

    async def drivetrainValueSelection():
        CURRENT_VALUE = 0

        def update(value):
            log('Select a value')
            log(f'Current >> {value}', 2, 1)

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
                return CURRENT_VALUE

            sys.sleep(0.01)

    async def waitValueSelection():
        CURRENT_VALUE = 0

        def update(value):
            log('Select a value')
            log(f'Current >> {value}', 2, 1)

        while True:
            if left():
                CURRENT_VALUE -= 1
                update(CURRENT_VALUE)
            elif right():
                CURRENT_VALUE += 1
                update(CURRENT_VALUE)
            elif select():
                return CURRENT_VALUE

            sys.sleep(0.01)

    async def turnValueSelection():
        CURRENT_VALUE = 0

        def update(value):
            log('Select a value')
            log(f'Current >> {value}', 2, 1)

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
                return CURRENT_VALUE

            sys.sleep(0.01)

    async def motorNameSelection():
        motors = configuration['motors']['other'].keys()

        CURRENT_MOTOR = motors[0]

        def update(motor):
            log('Select a motor')
            log(f'Current >> {motor}', 2, 1)

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
                return CURRENT_MOTOR

            sys.sleep(0.01)

    async def motorValueSelection(name):
        motor = configuration['motors']['other'][name]

        isDual = True if motor['type'] == 'dual' else False

        def update(value):
            log('Select a value')
            log(f'Current >> {value}', 2, 1)

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
                    return CURRENT_VALUE

    actionType = await actionSelection()

    if actionType == 'Move':
        value = await drivetrainValueSelection()
        action = {
            'type': 'move',
            'value': int(value)
        }

        actions.append(action)
    elif actionType == 'Wait':
        value = await waitValueSelection()
        action = {
            'type': 'wait',
            'value': int(value)
        }

        actions.append(action)
    elif actionType == 'Turn':
        value = await turnValueSelection()
        action = {
            'type': 'turn',
            'value': int(value)
        }

        actions.append(action)
    elif actionType == 'run_motor':
        name = await motorNameSelection()
        value = await motorValueSelection(name)
        action = {
            'type': 'run_motor',
            'name': name,
            'isDual': True if configuration['motors']['other'][name]['type'] == 'dual' else False,
            'motors': configuration['motors']['other'][name]['motors'],
            'value': int(value)
        }

        actions.append(action)


async def run():
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

        await main()

if __name__ == '__main__':
    print('Starting autonomous creator...')
    print('Press LD to generate code and exit')
    print('\n----------------------------------\n')
    asyncio.run(run())
    print('----------------------------------\n')
