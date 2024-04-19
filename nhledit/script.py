from .editor import NHLEditor
from .loader import load_nhl, save_nhl
from .nhl import ItemLayer


def parse_script(script_file):
    """Generator that parses commands from a script file, ignoring comments."""
    with open(script_file, "r") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()  # Efficiently remove comments and strip whitespace
            if line:
                yield line.split()


def print_commands(layer, group, command):
    """Prints the NHL layer details to the terminal based on the specified command and group setting.

    Args:
        layer (ItemLayer): The layer containing items to print.
        group (int): Number of item IDs per line.
        command (str): The prefix for each line, defaulting to '!drop'.
    """
    # Extract all item IDs from the layer; assuming a method exists that fetches all relevant item IDs
    item_ids = layer.get_items(include_variants=True)  # Adjust include_variants based on specific needs

    # Processing the item IDs in groups and printing each group on a new line with the specified command prefix
    for i in range(0, len(item_ids), group):
        grouped_items = item_ids[i : i + group]
        hex_items = " ".join(f"{item_id:04X}" for item_id in grouped_items)  # Convert each ID to hexadecimal
        print(f"{command} {hex_items}")  # Print the command followed by the grouped item IDs in hex


def run_script(base=None, output=None, *script_files, drop_group=4, drop_command="!"):
    """Executes commands from script files on a NHL file layer, optionally saving to an output file."""
    if base:
        try:
            layer = load_nhl(base)
        except FileNotFoundError:
            print(f"Warning: Base file {base} not found, starting with an empty layer.")
            layer = ItemLayer()
    else:
        layer = ItemLayer()

    editor = NHLEditor(layer)

    for script_file in script_files:
        for command in parse_script(script_file):
            editor.apply_command(command)

    if output:
        save_nhl(editor.layer, output)
    else:
        full_drop_command = drop_command + "drop"
        print_commands(editor.layer, drop_group, full_drop_command)
