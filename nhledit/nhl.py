from . import ITEM_EXTENSION, ITEM_DIY_RECIPE, ITEM_EMPTY, LAYER_WIDTH, LAYER_HEIGHT
import struct
from itertools import product


class ItemLayer:
    @classmethod
    def item_extension(self, item, x, y):
        item_base = item & 0xFFFF
        if item_base == ITEM_EMPTY:
            return item
        return x << 48 | y << 56 | item_base << 32 | ITEM_EXTENSION

    @classmethod
    def item_diy(self, item):
        return item << 32 | ITEM_DIY_RECIPE

    def __init__(self, data=None):
        self.struct = struct.Struct("<Q")
        if data is None:
            self.data = [ITEM_EMPTY] * (LAYER_WIDTH * LAYER_HEIGHT)
        else:
            self.data = [tile[0] for tile in self.struct.iter_unpack(data)]
        self.width = LAYER_WIDTH
        self.height = LAYER_HEIGHT

    def _get_offset(self, x, y):
        if not self.is_valid(x, y):
            raise ValueError("Invalid coordinate, outside of the map! (%d, %d)" % (x, y))
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
        """Set item to a coordinate and automatically apply extension."""
        if x % 2 != 0 or y % 2 != 0:
            raise ValueError("Coordinates must be even numbers! (%d, %d)" % (x, y))
        for ext_x, ext_y in product(range(width), range(height)):
            self._set_data(x + ext_x, y + ext_y, self.item_extension(item, ext_x, ext_y))
        self._set_data(x, y, item)

    def iter_bytes(self):
        for tile in self.data:
            yield self.struct.pack(tile)

    def get_items(self, include_variants=False):
        """Returns a list of item IDs from the layer, excluding items marked as empty or extensions,
        with an option to include variant data.

        Args:
            include_variants (bool): If True, includes variant data in the item ID.
                                    If False, returns only the base item ID.

        Returns:
            List[int]: A list of item IDs, optionally including variant data.
        """
        item_ids = []
        for x in range(self.width):
            for y in range(self.height):
                item_id = self.get_item(x, y)
                base_id = item_id & 0xFFFF  # Extract the base item ID to check against constants

                # Skip the item if it's an empty or an extension type
                if base_id == ITEM_EMPTY or base_id == ITEM_EXTENSION:
                    continue

                # Decide whether to append the full item ID or just the base item ID
                item_id = item_id if include_variants else base_id
                item_ids.append(item_id)

        return item_ids
