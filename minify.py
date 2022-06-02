import python_minifier
import sys

def minify(file):
  with open(file, 'r') as f:
    with open(file, 'w') as fi:
      fi.write(python_minifier.minify(f.read()))

for i in range(1, len(sys.argv)):
  minify(sys.argv[i])
