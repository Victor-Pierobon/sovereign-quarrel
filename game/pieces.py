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
    dist = cube_distance(start, target)
    if dist < 1 or dist > 3:
        return False

    # Must move in a straight line along one of the 6 hex axes
    if not is_orthogonal(start, target):
        return False

    # Target must always be empty — Striker jumps over pieces, never lands on them
    if grid.get_piece(target):
        return False

    path = cube_linedraw(start, target)
    enemy_count = 0
    for hex in path[1:-1]:
        piece = grid.get_piece(hex)
        if piece:
            if piece["owner"] != current_player:
                enemy_count += 1
                if enemy_count > 1:
                    return False  # Can only jump one enemy per move
            # Allied pieces are jumped over freely

    return True

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
    if dist < 1 or dist > 2:
        return False

    # Target must be empty (Sentry captures by jumping, not by landing)
    if grid.get_piece(target):
        return False

    path = cube_linedraw(start, target)
    # Allied pieces block movement; enemy pieces can be jumped (captured)
    for hex in path[1:-1]:
        piece = grid.get_piece(hex)
        if piece and piece["owner"] == current_player:
            return False

    return True