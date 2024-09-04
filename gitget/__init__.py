# See: https://stackoverflow.com/a/63731573
import sys
if not '-m' in sys.argv:
    from .cli import main
