from .constants import ITEM_DIY_RECIPE, ITEM_EMPTY
import re
import logging

re_context = re.compile(r'@([0-9]+),([0-9]+)(?:,([0-9]+))?(?:,([0-9]+))?(?:,([0-9]+))?(?:,([0-9]+))?(?:,([a-z,]+))?')
re_item = re.compile(r'([0-9a-fA-F]+)(?:[|]([0-9]+))?(?:[*]([0-9]+))?')
re_variant = re.compile(r'(?:([0-9])_([0-9])|NA)')

stacksize = {}

try:
    with open('res/stacksize.txt') as f:
        logging.info("stack size file loaded!")
        count = 0
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):  # Strip comments
                continue
            size, id = line.split()
            stacksize[int(id)] = int(size)
            count += 1
        logging.info("Total %s items loaded from stack size.", count)
except FileNotFoundError as e:
    logging.warn(e)


class ItemContext:
    def __init__(self, x=0, y=0, width=16, height=0, offset=0, flag0=0, settings=[]):
        self.x = x
        self.y = y
        self.width = max(width, 1)
        self.height = height
        self.offset = offset
        self.flag0 = flag0
        self.diy = 'diy' in settings
        self.hex = 'hex' in settings
        self.variants = 'variants' in settings
        self.fossil = 'fossil' in settings

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
        context_match = re_context.match(command)
        if context_match:
            return self.apply_context(context_match.groups())

        variant_match = re_variant.match(command)
        if variant_match:
            return self.apply_variant(variant_match.groups())

        item_match = re_item.match(command)
        if item_match:
            return self.apply_item(item_match.groups())

        raise ValueError('Invalid command: %s', command)

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
            arg2.extend(match_groups[-1].split(','))

        self.context = ItemContext(*arg1, flag0=flag0, settings=arg2)
        self.last_item = None

    def apply_item(self, match_items):
        if self.context.hex:
            item = int(match_items[0], 16)
        else:
            item = int(match_items[0])

        stack_size = max(0, int(match_items[1] or 1) - 1)
        count = max(0, int(match_items[2] or 1))

        item_base = item & 0xffff

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
        if item & 0x1f0000 == 0 and max_stack_size > 0:
            item |= max_stack_size << 32

        # Apply count number of items
        for _ in range(count):
            # Automatically increment variant code
            if self.last_item and self.context.variants and item_base == (self.last_item & 0xffff):
                item = item_base | (self.last_item & 0x1f0000 + 0x10000)
            self.last_item = item

            # Actual set item and increment counter
            self.layer.set_item(self.context.get_x(), self.context.get_y(), item)
            self.context.advance()

    def apply_variant(self, match_variant):
        if None not in match_variant:
            variant = int(match_variant[0])
            texture = int(match_variant[1])
            self.next_variant = variant << 32 | texture << 37
