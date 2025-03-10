class HexGrid:
    def __init__(self, radius=4):
        self.radius = radius
        self.tiles = self._generate_hexes()
        self.pieces = {}

    def _generate_hexes(self):
        hexes = []
        for x in range(-self.radius, self.radius + 1):
            for y in range(-self.radius, self.radius + 1):
                z = -x - y
                if abs(z) <= self.radius:
                    hexes.append((x, y, z))
        return hexes

    def is_valid_hex(self, hex):
        x, y, z = hex
        return (x + y + z == 0) and all(abs(coord) <= self.radius for coord in (x, y, z))

    def place_piece(self, hex, piece_type, owner):
        if self.is_valid_hex(hex):
            self.pieces[hex] = {"type": piece_type, "owner": owner}

    def get_piece(self, hex):
        return self.pieces.get(hex, None)

    def remove_piece(self, hex):
        if hex in self.pieces:
            del self.pieces[hex]

def cube_distance(hex_a, hex_b):
    return max(abs(hex_a[0] - hex_b[0]), 
              abs(hex_a[1] - hex_b[1]), 
              abs(hex_a[2] - hex_b[2]))

def cube_linedraw(start, end):
    n = cube_distance(start, end)
    results = []
    for i in range(n + 1):
        t = 1.0 / n * i
        x = start[0] * (1 - t) + end[0] * t
        y = start[1] * (1 - t) + end[1] * t
        z = -x - y
        results.append((round(x), round(y), round(z)))
    return results

def is_orthogonal(start, end):  # <-- ADD THIS FUNCTION
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dz = end[2] - start[2]
    return (abs(dx) == abs(dy)) or (abs(dy) == abs(dz)) or (abs(dz) == abs(dx))