import argparse
from nhledit import run_script

# Set up the argument parser
parser = argparse.ArgumentParser(description="Run scripts with provided base, output, and optional drop settings.")
parser.add_argument("files", nargs="*", help="Input files")
parser.add_argument("-b", "--base", help="Base file (optional)")
parser.add_argument("-o", "--output", help="Output file (optional)")
parser.add_argument("--drop-group", type=int, default=4, help="Number of outputs to drop in a group (default: 4)")
parser.add_argument("--drop-command", type=str, default="!", help="Prefix for drop command (default: '!')")

# Parse arguments
args = parser.parse_args()

# Execute the script with parsed arguments, including additional options
run_script(args.base, args.output, *args.files, drop_group=args.drop_group, drop_command=args.drop_command)
