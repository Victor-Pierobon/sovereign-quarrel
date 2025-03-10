from .grid import cube_distance, cube_linedraw, is_orthogonal

def validate_shield(start, target, grid, current_player):
    dist = cube_distance(start, target)
    
    # Regular move
    if dist == 1 and is_orthogonal(start, target):
        return not grid.get_piece(target)
    
    # Capture move
    if dist == 2 and is_orthogonal(start, target):
        path = cube_linedraw(start, target)
        mid = path[1]
        mid_piece = grid.get_piece(mid)
        return (
            mid_piece and 
            mid_piece["owner"] != current_player and 
            not grid.get_piece(target)
        )
    return False

def validate_striker(start, target, grid, current_player):
    if cube_distance(start, target) != 3:
        return False
    
    path = cube_linedraw(start, target)
    enemy_count = 0
    
    for hex in path[1:-1]:
        piece = grid.get_piece(hex)
        if piece:
            if piece["owner"] != current_player:
                enemy_count += 1
            elif piece["owner"] == current_player:
                continue  # Can jump friendlies
    return enemy_count <= 1 and not grid.get_piece(target)

def validate_caster(start, target, grid, current_player):
    dist = cube_distance(start, target)
    if dist > 5:
        return False
    
    path = cube_linedraw(start, target)
    enemy_count = 0
    
    for hex in path[1:-1]:
        piece = grid.get_piece(hex)
        if piece:
            if piece["owner"] != current_player:
                enemy_count += 1
            else:
                return False  # Blocked by friendly
    return enemy_count <= 1 and not grid.get_piece(target)

def validate_sentry(start, target, grid, current_player):
    dist = cube_distance(start, target)
    if dist not in (1, 2):
        return False
    
    path = cube_linedraw(start, target)
    for hex in path[1:-1]:
        if grid.get_piece(hex):
            return False
    return not grid.get_piece(target)