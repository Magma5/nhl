from nhledit import run_script
from glob import glob

run_script('base.nhl', 'acres.nhl', *glob('*.txt'))
