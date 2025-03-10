from flask import Flask, render_template, jsonify, request
from game.game_state import GameState

app = Flask(__name__)
game_state = GameState()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_board", methods=["GET"])
def get_board():
    # Convert tuple keys to strings and include tiles
    tiles = [f"{x},{y},{z}" for (x, y, z) in game_state.grid.tiles]
    pieces = {
        f"{x},{y},{z}": piece 
        for (x, y, z), piece in game_state.grid.pieces.items()
    }
    return jsonify({
        "tiles": tiles,
        "pieces": pieces
    })

@app.route("/move", methods=["POST"])
def handle_move():
    data = request.json
    result = game_state.handle_move(
        data["piece_type"],
        tuple(data["start_hex"]),
        tuple(data["target_hex"])
    )
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)