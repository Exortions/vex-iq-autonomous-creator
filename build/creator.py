configuration = {'default_power': 100, 'motors': {'drivetrain': {'left': {'port': 1, 'reverse_polarity': False}, 'right': {'port': 6, 'reverse_polarity': True}}, 'other': {}}, 'always_run': []}# Program start



import drivetrain as dt
import vexiq
import sys

joystick = vexiq.Joystick()
actions = []

left = vexiq.Motor(configuration['motors']['drivetrain']['left']['port'], configuration['motors']['drivetrain']['left']['reverse_polarity'])
right = vexiq.Motor(configuration['motors']['drivetrain']['right']['port'], configuration['motors']['drivetrain']['right']['reverse_polarity'])

drivetrain = dt.Drivetrain(left, right, 200, 176)

def save():
    print('Saved actions: \n----------------')
    print(str(actions))

    print('----------------')
    sleep(0.25)

def sleep(secs):
    sys.sleep(secs)

def select_action():
    available_actions = ['Move', 'Turn', 'Wait', 'Run Motor']

    action = available_actions[0]

    while True:
        vexiq.lcd_write('Action select (' + action + ')')
        if joystick.bLup():
            action = available_actions[(available_actions.index(action) - 1) % len(available_actions)]
        elif joystick.bRup():
            action = available_actions[(available_actions.index(action) + 1) % len(available_actions)]
        elif joystick.bLdown():
            save()
        elif joystick.bRdown():
            return action
        
        sleep(0.05)

def select_integer_value(minimum, maximum, on_decrease=None, on_increase=None, override_starting_value=None):
    value = minimum if override_starting_value is None else override_starting_value

    while True:
        vexiq.lcd_write('Value select (' + str(value) + ')')
        if joystick.bLup():
            if value - 1 < minimum:
                continue

            if on_decrease:
                on_decrease()

            value -= 1
        elif joystick.bRup():
            if value + 1 > maximum:
                continue

            if on_increase:
                on_increase()

            value += 1
        elif joystick.bLdown():
            save()
        elif joystick.bRdown():
            return value
        
        sleep(0.05)

def select_from_list(list):
    maximum = len(list) - 1

    value = 0

    while True:
        vexiq.lcd_write('Value select (' + list[value]['name'] + ')')
        if joystick.bLup():
            if value - 1 < 0:
                continue

            value -= 1
        elif joystick.bRup():
            if value + 1 > maximum:
                continue

            value += 1
        elif joystick.bLdown():
            save()
        elif joystick.bRdown():
            return value
        
        sleep(0.05)        

def moveOnDecrease():
    drivetrain.drive_until(int(configuration['default_power']), -10)

def moveOnIncrease():
    drivetrain.drive_until(int(configuration['default_power']), 10)

def turnOnDecrease():
    drivetrain.turn_until(int(configuration['default_power']), -1)

def turnOnIncrease():
    drivetrain.turn_until(int(configuration['default_power']), 1)

def run():
    action = select_action()

    sleep(0.2)

    if action == 'Move':
        value = select_integer_value(-100, 100, moveOnDecrease, moveOnIncrease, 0)

        sleep(0.1)

        actions.append({ 'type': 'move', 'value': value })

        print('Saved move action')
    elif action == 'Turn':
        value = select_integer_value(-360, 360, turnOnDecrease, turnOnIncrease, 0)
        
        sleep(0.1)
 
        actions.append({ 'type': 'turn', 'value': value })

        print('Saved turn action')
    elif action == 'Wait':
        value = select_integer_value(0, 100)
        
        sleep(0.1)

        actions.append({ 'type': 'wait', 'value': value })

        print('Saved wait action')
    elif action == 'Run Motor':
        if len(configuration['motors']['other']) == 0:
            vexiq.lcd_write('No motors found')
            sleep(2)
            return run()

        name = select_from_list(configuration['motors']['other'])
        value = select_integer_value(0, 100)
        actions.append({ 'type': 'run_motor', 'dual': motor['is_dual'], 'name': name, 'value': value })

        print('Saved run motor action')
    sleep(0.05)

    run()

def main():
    print('Welcome to the Autonomous Builder!')
    print('Press the left button to decrease a value')
    print('Press the right button to increase a value')
    print('Press the select button to save an action')
    print('Press the save button to print the list of actions to the console and exit.')
    run()

main()
