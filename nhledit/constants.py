ACRE_WIDTH = 32
ACRE_HEIGHT = 32

ACRE_COUNT_X = 7
ACRE_COUNT_Y = 6

LAYER_WIDTH = ACRE_WIDTH * ACRE_COUNT_X  # 224
LAYER_HEIGHT = ACRE_HEIGHT * ACRE_COUNT_Y  # 192

LAYER_TOTAL = LAYER_WIDTH * LAYER_HEIGHT  # 43008
ACRE_TOTAL = ACRE_WIDTH * ACRE_HEIGHT  # 512

ITEM_SIZE = 8
LAYER_SIZE = LAYER_TOTAL * ITEM_SIZE  # 344064

ITEM_EXTENSION = 0xfffd
ITEM_EMPTY = 0xfffe
ITEM_DIY_RECIPE = 0x16a1