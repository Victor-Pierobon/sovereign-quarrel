from .grid import HexGrid, cube_distance, cube_linedraw
from .pieces import validate_shield, validate_striker, validate_caster, validate_sentry

class GameState:
    def __init__(self):
        self.grid = HexGrid(radius=4)
        self.current_player = "Red"
        self.win_condition = None
        self.pending_true_win = None   # Set when a Sentry reaches a hold hex; confirmed next turn
        self.initialize_pieces()
        # True Win: advance your Sentry into the opponent's Caster ring (their inner defense)
        self.hold_hexes = {
            "White": [(-1, -3, 4), (0, -3, 3), (1, -4, 3)],   # Red's Caster starting hexes
            "Red":   [(1,  3, -4), (0,  3, -3), (-1, 4, -3)],  # White's Caster starting hexes
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

    def handle_move(self, start_hex, target_hex):
        start = tuple(start_hex)
        target = tuple(target_hex)
        piece = self.grid.get_piece(start)

        if not piece or piece["owner"] != self.current_player:
            return {"success": False, "message": "Invalid piece selection"}

        piece_type = piece["type"]
        validators = {
            "Sentry": validate_sentry,
            "Striker": validate_striker,
            "Caster": validate_caster,
            "Shield": validate_shield
        }

        if not validators[piece_type](start, target, self.grid, self.current_player):
            return {"success": False, "message": "Invalid move"}

        target_piece = self.grid.get_piece(target)
        if target_piece and target_piece["owner"] == self.current_player:
            return {"success": False, "message": "Can't move to ally position"}

        # Detect enemy Sentry capture BEFORE the board changes (target or mid-path jump)
        path = cube_linedraw(start, target)
        captured_sentry = (
            target_piece is not None
            and target_piece["owner"] != self.current_player
            and target_piece["type"] == "Sentry"
        )
        if not captured_sentry:
            for hex in path[1:-1]:
                p = self.grid.get_piece(hex)
                if p and p["owner"] != self.current_player and p["type"] == "Sentry":
                    captured_sentry = True
                    break

        # Execute move
        self.grid.remove_piece(start)
        self.grid.place_piece(target, piece_type, self.current_player)
        for hex in path[1:-1]:
            p = self.grid.get_piece(hex)
            if p and p["owner"] != self.current_player:
                self.grid.remove_piece(hex)

        opponent = "White" if self.current_player == "Red" else "Red"

        # Normal win: enemy Sentry captured
        if captured_sentry:
            self.win_condition = self.current_player
            return {"success": True, "game_over": True, "winner": self.current_player, "win_type": "normal"}

        # True win confirmation: opponent's Sentry was in a hold hex last turn and survived our move
        if self.pending_true_win == opponent and self._sentry_in_hold_for(opponent):
            self.win_condition = opponent
            self.pending_true_win = None
            return {"success": True, "game_over": True, "winner": opponent, "win_type": "true"}

        # Reset pending — either it was just confirmed above, or the threat was neutralised
        self.pending_true_win = None

        # Check if current player just landed their Sentry on a hold hex
        if self._sentry_in_hold_for(self.current_player):
            self.pending_true_win = self.current_player

        self.current_player = opponent
        result = {"success": True}
        if self.pending_true_win:
            result["pending_true_win"] = self.pending_true_win
        return result

    def _sentry_in_hold_for(self, player):
        """Return True if the given player's Sentry is on one of their hold hexes."""
        sentry_pos = next(
            (coords for coords, p in self.grid.pieces.items()
             if p["type"] == "Sentry" and p["owner"] == player),
            None
        )
        return sentry_pos is not None and sentry_pos in self.hold_hexes[player]

    def get_valid_moves(self, start_hex):
        start = tuple(start_hex)
        piece = self.grid.get_piece(start)
        if not piece or piece["owner"] != self.current_player:
            return []

        validators = {
            "Sentry": validate_sentry,
            "Striker": validate_striker,
            "Caster": validate_caster,
            "Shield": validate_shield
        }
        validator = validators.get(piece["type"])
        if not validator:
            return []

        valid = []
        for hex in self.grid.tiles:
            if hex == start:
                continue
            target_piece = self.grid.get_piece(hex)
            if target_piece and target_piece["owner"] == self.current_player:
                continue
            if validator(start, hex, self.grid, self.current_player):
                valid.append(list(hex))
        return valid