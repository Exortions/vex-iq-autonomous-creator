import json

OUTPUT_FILE = 'build/autonomous.py'
INPUT_FILE = 'config/input.json'
CONFIG_FILE = 'config.json'
class Compiler:
    def __init__(self) -> None:
        self.prep_input()

        self.load_config()
        self.load_input()

    def prep_input(self) -> None:
        text = ''

        with open(INPUT_FILE, 'r') as f:
            text = f.read()
        
        text = text.replace('\'', '"')
        text = text.replace('True', 'true')
        text = text.replace('False', 'false')
        text = text.replace('None', 'null')

        with open(INPUT_FILE, 'w') as f:
            f.write(text)

    def load_config(self) -> None:
        with open(CONFIG_FILE, 'r') as f:
            self.config = json.load(f)

    def load_input(self) -> None:
        with open(INPUT_FILE, 'r') as f:
            self.actions = json.load(f)

    def convert_move_action(self, value: int) -> str:
        return f'drivetrain.drive_until({int(self.config["default_power"])}, {value * 10})'

    def convert_turn_action(self, value: int) -> str:
        return f'drivetrain.turn_until({int(self.config["default_power"])}, {value})'
    
    def convert_wait_action(self, value: int) -> str:
        return f'sys.sleep({value / 100})'

    def convert_run_motor_action(self, name: str, dual: bool, value: int) -> str:
        code = ''
        
        if dual:
            motorOne = self.config['motors']['other'][name]['motors'][0]
            motorTwo = self.config['motors']['other'][name]['motors'][1]

            motorOneCode = f'vexiq.Motor({motorOne["port"]}, {motorOne["reverse_polarity"]}).run_until({int(self.config["default_power"])}, {value})'
            motorTwoCode = f'vexiq.Motor({motorTwo["port"]}, {motorTwo["reverse_polarity"]}).run_until({int(self.config["default_power"])}, {value})'

            code += f'{motorOneCode}\n{motorTwoCode}'
        else:
            motor = self.config['motors']['other'][name]
            
            code += f'vexiq.Motor({motor["port"]}, {motor["reverse_polarity"]}).run_until({int(self.config["default_power"])}, {value})'

        return code

    def convert_action(self, action: dict) -> str:
        code = ''
        
        action_type = str(action['type']).lower()
        value = int(action['value'])

        if action_type == 'move':
            code += self.convert_move_action(value)
        elif action_type == 'turn':
            code += self.convert_turn_action(value)
        elif action_type == 'wait':
            code += self.convert_wait_action(value)
        elif action_type == 'run_motor':
            code += self.convert_run_motor_action(action['name'], action['dual'], value)
        else:
            print(f'Unknown action type: {action_type}')

        code += '\n'

        return code

    def write(self) -> None:
        with open(OUTPUT_FILE, 'w') as f:
            f.write(self.code)

    def init_code(self) -> str:
        code = ''

        # Imports
        code += 'import drivetrain as dt\n'
        code += 'import vexiq\n'
        code += 'import sys\n\n'

        # Configuration

        drivetrain = self.config['motors']['drivetrain']

        left_motor = f'vexiq.Motor({str(drivetrain["left"]["port"])}, {str(drivetrain["left"]["reverse_polarity"])})'
        right_motor = f'vexiq.Motor({str(drivetrain["right"]["port"])}, {str(drivetrain["right"]["reverse_polarity"])})'

        code += f'drivetrain = dt.Drivetrain({left_motor}, {right_motor}, 200, 176)\n\n'

        # Initialize always running motors

        for runnable in self.config['always_run']:
            port = int(runnable['port'])
            reverse_polarity = bool(runnable['reverse_polarity'])
            power = int(runnable['power'])

            code += f'vexiq.Motor({port}, {reverse_polarity}).run({power})\n'

        code += '\n'

        return code
    
    def EOF(self) -> str:
        return '\n'

    def start(self) -> None:
        code = self.init_code()

        for action in self.actions:
            code += self.convert_action(action)
        
        code += self.EOF()

        self.code = code

        self.write()

def compile_to_python() -> None:
    compiler = Compiler()
    compiler.start()

compile_to_python()