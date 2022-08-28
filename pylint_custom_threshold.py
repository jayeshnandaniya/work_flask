import sys
from pylint import lint

THRESHOLD = 9.5

if len(sys.argv) < 2:
    raise RuntimeError("Module to evaluate needs to be the first argument")

run = lint.Run([sys.argv[1]], do_exit=False)
score = run.linter.stats['global_note']

if score < THRESHOLD:
    sys.exit(1)
