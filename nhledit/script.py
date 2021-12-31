from .editor import NHLEditor
from .loader import load_nhl, save_nhl
from .nhl import ItemLayer


def parse_script(script_file):
    with open(script_file, 'r') as f:
        for line in f:
            # strip out comments
            try:
                line = line[:line.index('#')]
            except ValueError:
                pass
            for command in line.strip().split():
                yield command


def run_script(input_file, output_file, *script_files):
    editor = NHLEditor(ItemLayer())
    if input_file is not None:
        try:
            editor = NHLEditor(load_nhl(input_file))
        except FileNotFoundError:
            pass

    for script in script_files:
        editor.reset_context()
        for command in parse_script(script):
            editor.apply_command(command)
    save_nhl(editor.layer, output_file)
