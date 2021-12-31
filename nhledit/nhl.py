from . import *
import struct
from itertools import product

class ItemLayer:
    @classmethod
    def item_extension(self, item, x, y):
        return x << 48 | y << 56 | (item & 0xffff) << 32 | ITEM_EXTENSION
    
    @classmethod
    def item_diy(self, item):
        return item << 32 | ITEM_DIY_RECIPE

    def __init__(self, data=None):
        self.struct = struct.Struct('<Q')
        if data is None:
            self.data = [ITEM_EMPTY] * (LAYER_WIDTH * LAYER_HEIGHT)
        else:
            self.data = [tile[0] for tile in self.struct.iter_unpack(data)]
        self.width = LAYER_WIDTH
        self.height = LAYER_HEIGHT

    def _get_offset(self, x, y):
        if not self.is_valid(x, y):
            raise ValueError('Invalid coordinate! (%d, %d)', x, y)
        return x * LAYER_HEIGHT + y

    def _set_data(self, x, y, item):
        """Write raw item data to the nhi"""
        offset = self._get_offset(x, y)
        self.data[offset] = item

    def is_valid(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_item(self, x, y):
        return self.data[self._get_offset(x, y)]

    def set_item(self, x, y, item, width=2, height=2):
        if x % 2 != 0 or y % 2 != 0:
            raise ValueError('Invalid coordinate to set item! %d, %d', x, y)
        for ext_x, ext_y in product(range(width), range(height)):
            self._set_data(x + ext_x, y + ext_y, self.item_extension(item, ext_x, ext_y))
        self._set_data(x, y, item)

    def iter_bytes(self):
        for tile in self.data:
            yield self.struct.pack(tile)

