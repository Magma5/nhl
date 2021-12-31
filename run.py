from nhledit import run_script
from glob import glob

run_script(None, 'acres.nhl', *glob('*.txt'))