from . import LAYER_SIZE
from .nhl import ItemLayer


def load_nhl(filename='acres.nhl'):
    with open(filename, 'rb') as f:
        data = f.read()
        if validate_nhl(data):
            return ItemLayer(data)


def save_nhl(item_layer, filename):
    with open(filename, 'wb') as f:
        for tile in item_layer.iter_bytes():
            f.write(tile)


def validate_nhl(data):
    if len(data) != LAYER_SIZE:
        raise ValueError('Incorrect layer file size!')
    return True
