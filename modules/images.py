class Grid:
    def __init__(self, tiles):
        self.tiles = tiles


def split_grid(image, tile_w, tile_h, overlap):
    row = [[0, image.width, image]]
    tiles = [(0, image.height, row)]
    return Grid(tiles)


def combine_grid(grid):
    row = grid.tiles[0][2]
    return row[0][2]


def save_image(image, outpath, basename, seed, prompt, fmt, info, p):
    pass
