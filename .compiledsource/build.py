import json
import os

def load_config():
    with open('config.json') as f:
        return json.load(f)

def build():
    file = 'creator.py'
    out = 'build/creator.py'

    code = ''

    with open(file) as f:
        code = f.read()
    
    config = load_config()

    if not os.path.exists('build'):
        os.makedirs('build')
    
    if not code.endswith('\n'):
        code += '\n'

    code = f'configuration = {config}{code}'

    # Delete all lines with comments
    code = '\n'.join([line for line in code.split('\n') if not line.startswith('#')])

    with open(out, 'w') as f:
        f.write(code)

build()