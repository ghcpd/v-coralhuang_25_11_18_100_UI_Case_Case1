"""Mock modules.images for testing"""
from PIL import Image


class GridTile:
    """Represents a tile in a grid"""
    def __init__(self, x, w, image):
        self.data = [x, w, image]
    
    def __getitem__(self, index):
        return self.data[index]
    
    def __setitem__(self, index, value):
        self.data[index] = value


class Grid:
    """Mock grid for tiling"""
    def __init__(self, tiles):
        self.tiles = tiles


def split_grid(image, tile_w, tile_h, overlap):
    """Mock split_grid function"""
    # Create a simple 2x2 grid for testing
    tiles = []
    rows = 2
    cols = 2
    
    for row in range(rows):
        y = row * tile_h
        h = tile_h
        row_tiles = []
        
        for col in range(cols):
            x = col * tile_w
            w = tile_w
            
            # Create a tile image
            tile_img = image.crop((
                min(x, image.width),
                min(y, image.height),
                min(x + w, image.width),
                min(y + h, image.height)
            ))
            
            row_tiles.append(GridTile(x, w, tile_img))
        
        tiles.append((y, h, row_tiles))
    
    return Grid(tiles)


def combine_grid(grid):
    """Mock combine_grid function"""
    # Get dimensions from first tile
    if not grid.tiles or not grid.tiles[0][2]:
        return Image.new("RGB", (512, 512))
    
    first_tile = grid.tiles[0][2][0]
    tile_w = first_tile[1]
    
    rows = len(grid.tiles)
    cols = len(grid.tiles[0][2]) if grid.tiles else 0
    
    # Calculate total dimensions
    total_w = 0
    total_h = 0
    
    for y, h, row_tiles in grid.tiles:
        total_h = max(total_h, y + h)
        for tile in row_tiles:
            x, w, _ = tile[0], tile[1], tile[2]
            total_w = max(total_w, x + w)
    
    # Create combined image
    combined = Image.new("RGB", (total_w, total_h))
    
    for y, h, row_tiles in grid.tiles:
        for tile in row_tiles:
            x, w, img = tile[0], tile[1], tile[2]
            if img:
                combined.paste(img, (x, y))
    
    return combined


def save_image(image, path, filename, seed, prompt, format, info=None, p=None):
    """Mock save_image function"""
    pass
