from .grid import HexGrid, cube_distance, cube_linedraw
from .pieces import validate_shield, validate_striker, validate_caster, validate_sentry

class GameState:
    def __init__(self):
        self.grid = HexGrid(radius=4)
        self.current_player = "Red"
        self.win_condition = None
        self.initialize_pieces()
        self.hold_hexes = {
            "White": [(0, -4, 4), (-4, 0, 4), (4, 0, -4)],  # Red's side
            "Red": [(0, 4, -4), (-4, 4, 0), (4, -4, 0)]     # White's side
        }

    def initialize_pieces(self):
        # Player 1 (White) - North side
        self._place_white_pieces()
        
        # Player 2 (Red) - South side
        self._place_red_pieces()

    def _place_white_pieces(self):
        """White pieces arranged around (0,4,-4)"""
        # Sentry (edge)
        self.grid.place_piece((0, 4, -4), "Sentry", "White")
        
        # Casters (3 around Sentry)
        self.grid.place_piece((1, 3, -4), "Caster", "White")
        self.grid.place_piece((0, 3, -3), "Caster", "White")
        self.grid.place_piece((-1, 4, -3), "Caster", "White")
        
        # Strikers (5 around Casters)
        self.grid.place_piece((2, 2, -4), "Striker", "White")
        self.grid.place_piece((1, 2, -3), "Striker", "White")
        self.grid.place_piece((0, 2, -2), "Striker", "White")
        self.grid.place_piece((-1, 3, -2), "Striker", "White")
        self.grid.place_piece((-2, 4, -2), "Striker", "White")
        
        # Shields (7 around Strikers)
        self.grid.place_piece((3, 1, -4), "Shield", "White")
        self.grid.place_piece((2, 1, -3), "Shield", "White")
        self.grid.place_piece((1, 1, -2), "Shield", "White")
        self.grid.place_piece((0, 1, -1), "Shield", "White")
        self.grid.place_piece((-1, 2, -1), "Shield", "White")
        self.grid.place_piece((-2, 3, -1), "Shield", "White")
        self.grid.place_piece((-3, 4, -1), "Shield", "White")

    def _place_red_pieces(self):
        """Red pieces arranged around (0,-4,4)"""
        # Sentry (edge)
        self.grid.place_piece((0, -4, 4), "Sentry", "Red")
        
        # Casters (3 around Sentry)
        self.grid.place_piece((-1, -3, 4), "Caster", "Red")
        self.grid.place_piece((0, -3, 3), "Caster", "Red")
        self.grid.place_piece((1, -4, 3), "Caster", "Red")
        
        # Strikers (5 around Casters)
        self.grid.place_piece((-2, -2, 4), "Striker", "Red")
        self.grid.place_piece((-1, -2, 3), "Striker", "Red")
        self.grid.place_piece((0, -2, 2), "Striker", "Red")
        self.grid.place_piece((1, -3, 2), "Striker", "Red")
        self.grid.place_piece((2, -4, 2), "Striker", "Red")
        
        # Shields (7 around Strikers)
        self.grid.place_piece((-3, -1, 4), "Shield", "Red")
        self.grid.place_piece((-2, -1, 3), "Shield", "Red")
        self.grid.place_piece((-1, -1, 2), "Shield", "Red")
        self.grid.place_piece((0, -1, 1), "Shield", "Red")
        self.grid.place_piece((1, -2, 1), "Shield", "Red")
        self.grid.place_piece((2, -3, 1), "Shield", "Red")
        self.grid.place_piece((3, -4, 1), "Shield", "Red")

    def handle_move(self, piece_type, start_hex, target_hex):
        start = tuple(start_hex)
        target = tuple(target_hex)
        piece = self.grid.get_piece(start)
        
        if not piece or piece["owner"] != self.current_player:
            return {"success": False, "message": "Invalid piece selection"}

        # Validate move pattern
        validators = {
            "Sentry": validate_sentry,
            "Striker": validate_striker,
            "Caster": validate_caster,
            "Shield": validate_shield
        }

        if not validators[piece_type](start, target, self.grid, self.current_player):
            return {"success": False, "message": "Invalid move"}

        # Check target space occupation
        target_piece = self.grid.get_piece(target)
        if target_piece and target_piece["owner"] == self.current_player:
            return {"success": False, "message": "Can't move to ally position"}

        # Perform move
        self.grid.remove_piece(start)
        self.grid.place_piece(target, piece_type, self.current_player)

        # Check captures along path
        path = cube_linedraw(start, target)
        for hex in path[1:-1]:  # Exclude start and end positions
            piece = self.grid.get_piece(hex)
            if piece and piece["owner"] != self.current_player:
                self.grid.remove_piece(hex)

        # Check win conditions
        if self.check_win_conditions(target):
            return {"success": True, "game_over": True, "winner": self.current_player}

        # Switch turns
        self.current_player = "White" if self.current_player == "Red" else "Red"
        return {"success": True}

    def check_win_conditions(self, target_hex):
        # Immediate win condition (captured enemy Sentry)
        target_piece = self.grid.get_piece(target_hex)
        if target_piece and target_piece["type"] == "Sentry":
            return True

        # True victory condition (Sentry in enemy hold hex)
        sentry_pos = next(
            (coords for coords, piece in self.grid.pieces.items()
             if piece["type"] == "Sentry" and piece["owner"] == self.current_player),
            None
        )
        
        if sentry_pos and sentry_pos in self.hold_hexes[self.current_player]:
            return True

        return False