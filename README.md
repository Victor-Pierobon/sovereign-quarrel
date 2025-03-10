# Sovereign Quarel Board Game - Web Game

## About

Sovereign Quarel is a two-player strategy board game inspired by "The Beginning After The End" novel series.  This web-based implementation is a simplified version of the fictional game, focusing on core gameplay mechanics and strategic piece movement.

## Game Rules (v1.0)

**Objective:**

*   **Normal Win:** Capture your opponent's **Sentry** piece.
*   **True Win:** Move your **Sentry** piece to any of your opponent's designated **Hold hexes** (corner hexes on *their* side of the board).

**Equipment:**

*   Hexagonal Game Board (7 hexes per side)
*   Player 1 Pieces (1 Sentry, 3 Casters, 5 Strikers, 7 Shields - white color)
*   Player 2 Pieces (1 Sentry, 3 Casters, 5 Strikers, 7 Shields - Red color)


Red takes the first turn(Caera says in the novel that tradicionaly white goes second).

**Gameplay:**

1.  **Turns:** Players alternate turns.
2.  **Movement:** On your turn, you *must* move one of your pieces according to its movement rules.
3.  **Piece Movement Rules:**

    *   **Sentry (Circle/Hexagon):** Moves 1-2 hexes in *any* direction (orthogonal or diagonal) per turn.
    *   **Strikers (Line/Sword):** Moves in a straight line 3 hexes in any direction (orthogonal or diagonal) per turn, adicionaly it can jump friendly pieces too.
    *   **Casters (Triangle/Fire):** Moves anywhere within **5 hexes distance** (radius) in any direction per turn. *Cannot jump over friendly pieces.*
    *   **Shields (Square/Shield):** Moves **1 hex orthogonally** (up, down, left, right) per turn. *Can jump over adjacent enemy pieces in orthogonal directions if there is an empty hex beyond to capture an enemy piece by jumping.*

4.  **Capture:** Any piece can capture via jumping over the enemy piece, casters can only capture one piece at a time.


**Winning the Game:**

*   **Normal Win:** Capture the opponent's **Sentry** piece.
*   **True Win:** Move your **Sentry** piece to *any* of your opponent's designated **Hold hexes** (corner hexes on their side of the board).

# Sovereign Quarrel - Web Implementation

A Python-based web adaptation of the strategic board game from *The Beginning After The End*.



## Author

[ Victor Pierobon] (Based on inspiration from "The Beginning After The End" by TurtleMe)

---