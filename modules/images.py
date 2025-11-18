"""
Mock modules.images for testing purposes.
"""


class GridTiles:
    """Mock grid tiles structure."""
    def __init__(self, tiles):
        self.tiles = tiles


def split_grid(img, tile_w, tile_h, overlap):
    """
    Mock split_grid function.
    Returns a GridTiles object with a simple tile structure.
    Note: Returns lists instead of tuples so they can be modified.
    """
    tiles = []
    y = 0
    while y < img.height:
        h = min(tile_h, img.height - y)
        row = []
        x = 0
        while x < img.width:
            w = min(tile_w, img.width - x)
            tile_img = img.crop((x, y, x + w, y + h))
            # Use list instead of tuple so tiledata[2] can be modified
            row.append([x, w, tile_img])
            x += tile_w - overlap
        # Use list instead of tuple for consistency
        tiles.append([y, h, row])
        y += tile_h - overlap
    
    return GridTiles(tiles)


def combine_grid(grid):
    """
    Mock combine_grid function.
    Combines tiles back into a single image.
    """
    from PIL import Image
    
    if not grid.tiles:
        return Image.new("RGB", (512, 512))
    
    # Calculate total dimensions
    max_width = 0
    total_height = 0
    
    for tile in grid.tiles:
        y, h, row = tile[0], tile[1], tile[2]
        row_width = sum(t[1] for t in row)
        max_width = max(max_width, row_width)
        total_height += h
    
    # Create combined image
    combined = Image.new("RGB", (max_width, total_height))
    current_y = 0
    
    for tile in grid.tiles:
        y, h, row = tile[0], tile[1], tile[2]
        current_x = 0
        for tiledata in row:
            x, w, img = tiledata[0], tiledata[1], tiledata[2]
            combined.paste(img, (current_x, current_y))
            current_x += w
        current_y += h
    
    return combined


def save_image(img, path, basename, seed, prompt, format, info=None, p=None):
    """Mock save_image function."""
    import os
    os.makedirs(path, exist_ok=True)
    filename = f"{basename}_{seed}.{format}"
    filepath = os.path.join(path, filename)
    img.save(filepath)
    return filepath

