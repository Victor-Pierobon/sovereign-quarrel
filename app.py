from flask import Flask, render_template, jsonify, request
from game.game_state import GameState

app = Flask(__name__)
game_state = GameState()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_board", methods=["GET"])
def get_board():
    tiles = [f"{x},{y},{z}" for (x, y, z) in game_state.grid.tiles]
    pieces = {
        f"{x},{y},{z}": piece
        for (x, y, z), piece in game_state.grid.pieces.items()
    }
    hold_hexes = {
        player: [f"{h[0]},{h[1]},{h[2]}" for h in hexes]
        for player, hexes in game_state.hold_hexes.items()
    }
    return jsonify({
        "tiles": tiles,
        "pieces": pieces,
        "current_player": game_state.current_player,
        "winner": game_state.win_condition,
        "hold_hexes": hold_hexes,
        "pending_true_win": game_state.pending_true_win,
    })

@app.route("/move", methods=["POST"])
def handle_move():
    data = request.json
    if not data:
        return jsonify({"success": False, "message": "No data provided"}), 400

    start = data.get("start_hex")
    target = data.get("target_hex")
    if not start or not target or len(start) != 3 or len(target) != 3:
        return jsonify({"success": False, "message": "Invalid hex coordinates"}), 400

    if game_state.win_condition:
        return jsonify({"success": False, "message": "Game is already over"}), 400

    result = game_state.handle_move(start, target)
    return jsonify(result)

@app.route("/valid_moves", methods=["POST"])
def valid_moves():
    data = request.json
    if not data:
        return jsonify({"moves": []}), 400
    start = data.get("start_hex")
    if not start or len(start) != 3:
        return jsonify({"moves": []}), 400
    moves = game_state.get_valid_moves(start)
    return jsonify({"moves": moves})

@app.route("/reset", methods=["POST"])
def reset():
    global game_state
    game_state = GameState()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(debug=True)