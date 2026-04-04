const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const HEX_SIZE = 40;
const ORIGIN_X = canvas.width / 2;
const ORIGIN_Y = canvas.height / 2;

let selectedPiece = null;
let boardData = null;
let validMoves = new Set();

// ── Coordinate helpers ──────────────────────────────────────────────────────

function cubeToPixel(x, y, z) {
    return {
        x: ORIGIN_X + HEX_SIZE * (3 / 2 * x),
        y: ORIGIN_Y + HEX_SIZE * (Math.sqrt(3) / 2 * x + Math.sqrt(3) * y)
    };
}

function cubeRound(x, y, z) {
    let rx = Math.round(x), ry = Math.round(y), rz = Math.round(z);
    const xd = Math.abs(rx - x), yd = Math.abs(ry - y), zd = Math.abs(rz - z);
    if (xd > yd && xd > zd) rx = -ry - rz;
    else if (yd > zd) ry = -rx - rz;
    else rz = -rx - ry;
    return [rx, ry, rz];
}

function pixelToCube(x, y) {
    const mx = x - ORIGIN_X;
    const my = y - ORIGIN_Y;
    const q = (mx * (2 / 3)) / HEX_SIZE;
    const r = (-mx / 3 + my / Math.sqrt(3)) / HEX_SIZE;
    return cubeRound(q, r, -q - r);
}

// ── Drawing primitives ──────────────────────────────────────────────────────

function hexPath(center, size = HEX_SIZE) {
    ctx.beginPath();
    for (let i = 0; i < 6; i++) {
        const angle = Math.PI / 3 * i;
        ctx.lineTo(center.x + size * Math.cos(angle), center.y + size * Math.sin(angle));
    }
    ctx.closePath();
}

// ── Piece drawing ───────────────────────────────────────────────────────────

function drawPiece(x, y, z, piece) {
    const center = cubeToPixel(x, y, z);
    const isRed  = piece.owner === "Red";
    const fill   = isRed ? "#c0392b" : "#d9cfc0";
    const stroke = isRed ? "#7b241c" : "#8a7d6a";
    const glow   = isRed ? "rgba(192,57,43,0.55)" : "rgba(217,207,192,0.5)";

    ctx.save();
    ctx.fillStyle   = fill;
    ctx.strokeStyle = stroke;
    ctx.lineWidth   = 1.8;
    ctx.shadowColor = glow;
    ctx.shadowBlur  = 7;

    switch (piece.type) {

        case 'Sentry': {
            // Three-toothed crown
            const w = HEX_SIZE * 0.28;
            const bandBot = center.y + HEX_SIZE * 0.23;
            const bandTop = center.y + HEX_SIZE * 0.04;
            const sideY   = center.y - HEX_SIZE * 0.18;
            const centerY = center.y - HEX_SIZE * 0.38;

            ctx.beginPath();
            ctx.moveTo(center.x - w,        bandBot);
            ctx.lineTo(center.x + w,        bandBot);
            ctx.lineTo(center.x + w,        bandTop);
            ctx.lineTo(center.x + w * 0.72, sideY);
            ctx.lineTo(center.x + w * 0.42, bandTop);
            ctx.lineTo(center.x,            centerY);
            ctx.lineTo(center.x - w * 0.42, bandTop);
            ctx.lineTo(center.x - w * 0.72, sideY);
            ctx.lineTo(center.x - w,        bandTop);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();
            break;
        }

        case 'Caster': {
            // Teardrop flame with inner highlight
            const tipY  = center.y - HEX_SIZE * 0.42;
            const baseY = center.y + HEX_SIZE * 0.28;
            const fw    = HEX_SIZE * 0.27;

            ctx.beginPath();
            ctx.moveTo(center.x, tipY);
            ctx.bezierCurveTo(
                center.x + fw * 1.3, center.y - HEX_SIZE * 0.15,
                center.x + fw,       baseY,
                center.x,            baseY
            );
            ctx.bezierCurveTo(
                center.x - fw,       baseY,
                center.x - fw * 1.3, center.y - HEX_SIZE * 0.15,
                center.x,            tipY
            );
            ctx.fill();
            ctx.stroke();

            // Inner flame highlight
            ctx.shadowBlur = 10;
            ctx.shadowColor = isRed ? "rgba(243,156,18,0.8)" : "rgba(180,210,255,0.8)";
            ctx.fillStyle   = isRed ? "#e67e22" : "#aed6f1";
            const iw = fw * 0.48;
            const itip = tipY + HEX_SIZE * 0.14;
            const ibase = baseY - HEX_SIZE * 0.14;
            ctx.beginPath();
            ctx.moveTo(center.x, itip);
            ctx.bezierCurveTo(
                center.x + iw, center.y - HEX_SIZE * 0.05,
                center.x + iw * 0.6, ibase,
                center.x,            ibase
            );
            ctx.bezierCurveTo(
                center.x - iw * 0.6, ibase,
                center.x - iw, center.y - HEX_SIZE * 0.05,
                center.x,            itip
            );
            ctx.fill();
            break;
        }

        case 'Striker': {
            // Sword: pointed blade, cross-guard, handle, pommel
            const tipY   = center.y - HEX_SIZE * 0.42;
            const guardY = center.y - HEX_SIZE * 0.01;
            const bw     = HEX_SIZE * 0.072;
            const gw     = HEX_SIZE * 0.27;
            const gh     = HEX_SIZE * 0.065;
            const hw     = HEX_SIZE * 0.052;
            const hh     = HEX_SIZE * 0.21;

            // Blade
            ctx.beginPath();
            ctx.moveTo(center.x,      tipY);
            ctx.lineTo(center.x + bw, guardY);
            ctx.lineTo(center.x - bw, guardY);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Cross-guard
            ctx.beginPath();
            ctx.rect(center.x - gw, guardY - gh / 2, gw * 2, gh);
            ctx.fill();
            ctx.stroke();

            // Handle
            ctx.beginPath();
            ctx.rect(center.x - hw, guardY + gh / 2, hw * 2, hh);
            ctx.fill();
            ctx.stroke();

            // Pommel
            ctx.beginPath();
            ctx.arc(center.x, guardY + gh / 2 + hh, hw * 1.6, 0, Math.PI * 2);
            ctx.fill();
            ctx.stroke();
            break;
        }

        case 'Shield': {
            // Heraldic shield: flat top, straight sides, curved bottom to a point
            const sw   = HEX_SIZE * 0.30;
            const topY = center.y - HEX_SIZE * 0.30;
            const midY = center.y + HEX_SIZE * 0.06;
            const botY = center.y + HEX_SIZE * 0.38;

            ctx.beginPath();
            ctx.moveTo(center.x - sw, topY);
            ctx.lineTo(center.x + sw, topY);
            ctx.lineTo(center.x + sw, midY);
            ctx.quadraticCurveTo(center.x + sw, botY, center.x, botY);
            ctx.quadraticCurveTo(center.x - sw, botY, center.x - sw, midY);
            ctx.closePath();
            ctx.fill();
            ctx.stroke();

            // Emblem line across the shield top third
            ctx.strokeStyle = stroke;
            ctx.lineWidth = 1.2;
            ctx.shadowBlur = 0;
            const divY = topY + (midY - topY) * 0.45;
            ctx.beginPath();
            ctx.moveTo(center.x - sw + 2, divY);
            ctx.lineTo(center.x + sw - 2, divY);
            ctx.stroke();
            break;
        }
    }

    ctx.restore();
}

// ── Status bar ──────────────────────────────────────────────────────────────

function updateStatus(data) {
    const el = document.getElementById('status');
    if (!el) return;
    if (data.winner) {
        el.textContent = `★  ${data.winner} wins!  ★`;
    } else if (data.pending_true_win) {
        const defender = data.current_player;
        el.textContent = `⚠  ${data.pending_true_win}'s Sentry is in the inner ring! ${defender} must capture it or lose!`;
    } else if (selectedPiece) {
        el.textContent = `${data.current_player}'s turn — choose destination  (click piece again to cancel)`;
    } else {
        el.textContent = `${data.current_player}'s turn — select a piece`;
    }
}

// ── Board rendering ─────────────────────────────────────────────────────────

function renderBoard(data) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const holdHexes  = data.hold_hexes || {};
    const whiteHolds = new Set(holdHexes["White"] || []);
    const redHolds   = new Set(holdHexes["Red"]   || []);
    const selKey     = selectedPiece ? selectedPiece.coords.join(',') : null;

    data.tiles.forEach(hexStr => {
        const [x, y, z] = hexStr.split(',').map(Number);
        const center = cubeToPixel(x, y, z);

        // ── Base hex fill ──
        hexPath(center);
        ctx.fillStyle = "#121e2b";
        ctx.fill();

        // ── Tint layers ──
        if (whiteHolds.has(hexStr)) {
            hexPath(center);
            ctx.fillStyle = "rgba(217,207,192,0.10)";
            ctx.fill();
        }
        if (redHolds.has(hexStr)) {
            hexPath(center);
            ctx.fillStyle = "rgba(192,57,43,0.12)";
            ctx.fill();
        }
        if (hexStr === selKey) {
            hexPath(center);
            ctx.fillStyle = "rgba(212,172,13,0.30)";
            ctx.fill();
        }
        if (validMoves.has(hexStr)) {
            hexPath(center);
            ctx.fillStyle = data.pieces[hexStr]
                ? "rgba(192,57,43,0.38)"
                : "rgba(39,174,96,0.28)";
            ctx.fill();
        }

        // ── Hex border ──
        hexPath(center);
        ctx.strokeStyle = "#1e3d5c";
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // ── Hold hex inner ring marker ──
        if (whiteHolds.has(hexStr) || redHolds.has(hexStr)) {
            const ringColor = whiteHolds.has(hexStr)
                ? "rgba(217,207,192,0.55)"
                : "rgba(192,57,43,0.55)";
            hexPath(center, HEX_SIZE * 0.8);
            ctx.strokeStyle = ringColor;
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    });

    // ── Pieces drawn on top ──
    Object.entries(data.pieces).forEach(([coords, piece]) => {
        const [x, y, z] = coords.split(',').map(Number);
        drawPiece(x, y, z, piece);
    });

    updateStatus(data);
}

// ── Server helpers ──────────────────────────────────────────────────────────

async function selectPiece(coords, pieceData) {
    selectedPiece = { coords, type: pieceData.type };
    validMoves = new Set();
    renderBoard(boardData);

    const res = await fetch('/valid_moves', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ start_hex: coords })
    });
    const result = await res.json();
    validMoves = new Set(result.moves.map(m => m.join(',')));
    renderBoard(boardData);
}

function drawBoard() {
    fetch('/get_board')
        .then(r => r.json())
        .then(data => {
            boardData = data;
            renderBoard(data);
        });
}

// ── Input handling ──────────────────────────────────────────────────────────

canvas.addEventListener('click', async (e) => {
    if (boardData && boardData.winner) return;

    const rect   = canvas.getBoundingClientRect();
    const scaleX = canvas.width  / rect.width;
    const scaleY = canvas.height / rect.height;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top)  * scaleY;
    const [q, r, s] = pixelToCube(x, y);
    const coordStr  = `${q},${r},${s}`;

    if (selectedPiece) {
        if (coordStr === selectedPiece.coords.join(',')) {
            selectedPiece = null;
            validMoves = new Set();
            renderBoard(boardData);
            return;
        }
        if (boardData.pieces[coordStr] &&
            boardData.pieces[coordStr].owner === boardData.current_player) {
            await selectPiece([q, r, s], boardData.pieces[coordStr]);
            return;
        }
        const res = await fetch('/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_hex: selectedPiece.coords, target_hex: [q, r, s] })
        });
        const result = await res.json();
        selectedPiece = null;
        validMoves = new Set();
        if (result.success) {
            drawBoard();
        } else {
            renderBoard(boardData);
        }
    } else {
        if (boardData && boardData.pieces[coordStr] &&
            boardData.pieces[coordStr].owner === boardData.current_player) {
            await selectPiece([q, r, s], boardData.pieces[coordStr]);
        }
    }
});

document.getElementById('resetBtn').addEventListener('click', () => {
    fetch('/reset', { method: 'POST' }).then(() => {
        selectedPiece = null;
        validMoves = new Set();
        drawBoard();
    });
});

drawBoard();
