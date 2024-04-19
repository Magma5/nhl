from .constants import ITEM_DIY_RECIPE, ITEM_EMPTY
import re
import logging

# Regex to parse item context strings starting with '@'. Captures x, y coordinates, width, height, offset,
# a hexadecimal flag0, and a comma-separated list of settings. Used to initialize ItemContext objects with detailed positioning and behavioral settings.
re_context = re.compile(r"@([0-9]+),([0-9]+)(?:,([0-9]+))?(?:,([0-9]+))?(?:,([0-9]+))?(?:,([0-9a-fA-F]+))?(?:,([a-z,]+))?")
# Regex to parse item strings consisting of a hexadecimal ID, optionally followed by a stack size (preceded by '|') and a count (preceded by '*'). These values influence item representation and behavior based on context settings.
re_item = re.compile(r"([0-9a-fA-F]+)(?:[|]([0-9]+))?(?:[*]([0-9]+))?")
# Regex to parse variant strings, either as 'NA' or as two single digits separated by an underscore, representing variant and texture codes for items. Used to manipulate item's bit representation for variants.
re_variant = re.compile(r"(?:([0-9])_([0-9])|NA)")

stacksize = {}

try:
    with open("res/stacksize.txt") as f:
        logging.info("Stack size file loaded!")
        count = 0
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):  # Skip empty lines and comments
                stack_size, item_id = line.split()
                stacksize[int(item_id)] = int(stack_size)
                count += 1
        logging.info(f"Total {count} items loaded from stack size file.")
except FileNotFoundError as e:
    logging.warning(f"File not found: {e}")


class ItemContext:
    def __init__(self, x=0, y=0, width=16, height=0, offset=0, flag0=0, settings=[]):
        self.x = x
        self.y = y
        self.width = max(width, 1)
        self.height = height
        self.offset = offset
        self.flag0 = flag0
        self.diy = "diy" in settings
        self.hex = "hex" in settings
        self.variants = "variants" in settings
        self.fossil = "fossil" in settings

    def advance(self):
        self.offset += 1

    def get_x(self):
        return self.x + (self.offset % self.width) * 2

    def get_y(self):
        return self.y + (self.offset // self.width) * 2


class NHLEditor:
    def __init__(self, item_layer):
        self.layer = item_layer
        self.context = ItemContext()
        self.last_item = None
        self.next_variant = 0

    def reset_context(self):
        self.context = ItemContext()

    def apply_script(self, commands):
        for command in commands:
            self.apply_command(command)

    def apply_command(self, command):
        if not command:
            return  # Skip empty command

        if len(command) == 1:
            # Single field command
            if command[0].startswith("@"):
                context_match = re_context.match(command[0])
                if context_match:
                    self.apply_context(context_match.groups())
                else:
                    raise ValueError(f"Invalid context command format: {command[0]}")
            else:
                item_match = re_item.match(command[0])
                if item_match:
                    self.apply_item(item_match.groups())
                else:
                    raise ValueError(f"Invalid item command format: {command[0]}")

        elif len(command) == 2:
            # Two fields, assumed to be variant_id and item_id
            variant_match = re_variant.match(command[0])
            item_match = re_item.match(command[1])
            if variant_match and item_match:
                self.apply_variant(variant_match.groups())
                self.apply_item(item_match.groups())
            else:
                raise ValueError(f"Invalid variant or item ID format: {command}")

        elif len(command) > 2:
            # More complex command, third-last is variant_id, second-last is item_id
            variant_id = command[-3]
            item_id = command[-2]
            variant_match = re_variant.match(variant_id)
            if variant_match:
                self.apply_variant(variant_match.groups())
            elif not variant_id.isdigit():  # Check if variant ID is not just a single integer
                raise ValueError(f"Invalid variant ID format: {variant_id}")
            item_match = re_item.match(item_id)
            if item_match:
                self.apply_item(item_match.groups())
            else:
                raise ValueError(f"Invalid item ID format: {item_id}")

    def apply_context(self, match_groups):
        arg1 = []
        for x in match_groups[:5]:
            if x is None:
                break
            arg1.append(int(x))

        # Convert flag0
        flag0 = 0
        if match_groups[5] is not None:
            flag0 = int(match_groups[5], 16)

        # Convert additional flags
        arg2 = []
        if match_groups[-1] is not None:
            arg2.extend(match_groups[-1].split(","))

        self.context = ItemContext(*arg1, flag0=flag0, settings=arg2)
        self.last_item = None

    def apply_item(self, match_items):
        if self.context.hex:
            item = int(match_items[0], 16)
        else:
            item = int(match_items[0])

        stack_size = max(0, int(match_items[1] or 1) - 1)
        count = max(0, int(match_items[2] or 1))

        item_base = item & 0xFFFF

        # Set flag0 and stack size or variant
        item |= self.context.flag0 << 16
        item |= stack_size << 32
        if self.next_variant > 0:
            item |= self.next_variant
            self.next_variant = 0

        # Convert item to DIY recipe
        if self.context.diy:
            item = item_base << 32 | ITEM_DIY_RECIPE

        # Set invalid item to empty item
        if item_base == 0:
            item = ITEM_EMPTY

        # Apply default stack size
        max_stack_size = stacksize.get(item_base, 1) - 1
        if item & 0x1F0000 == 0 and max_stack_size > 0:
            item |= max_stack_size << 32

        # Apply count number of items
        for _ in range(count):
            # Automatically increment variant code
            if self.last_item and self.context.variants and item_base == (self.last_item & 0xFFFF):
                item = item_base | (self.last_item & 0x1F0000 + 0x10000)
            self.last_item = item

            # Actual set item and increment counter
            self.layer.set_item(self.context.get_x(), self.context.get_y(), item)
            self.context.advance()

    def apply_variant(self, match_variant):
        if None not in match_variant:
            variant = int(match_variant[0])
            texture = int(match_variant[1])
            self.next_variant = variant << 32 | texture << 37
