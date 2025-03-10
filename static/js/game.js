const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const HEX_SIZE = 40;
const ORIGIN_X = canvas.width / 2;
const ORIGIN_Y = canvas.height / 2;
let selectedPiece = null;

function cubeToPixel(x, y, z) {
    return {
        x: ORIGIN_X + HEX_SIZE * (3/2 * x),
        y: ORIGIN_Y + HEX_SIZE * (Math.sqrt(3)/2 * x + Math.sqrt(3) * y)
    };
}

function drawHex(x, y, z) {
    const center = cubeToPixel(x, y, z);
    ctx.beginPath();
    for(let i = 0; i < 6; i++) {
        const angle = Math.PI/3 * i;
        const xPos = center.x + HEX_SIZE * Math.cos(angle);
        const yPos = center.y + HEX_SIZE * Math.sin(angle);
        ctx.lineTo(xPos, yPos);
    }
    ctx.closePath();
    ctx.strokeStyle = "#95a5a6";
    ctx.lineWidth = 2;
    ctx.stroke();
}

function cubeRound(x, y, z) {
    let rx = Math.round(x);
    let ry = Math.round(y);
    let rz = Math.round(z);

    const xDiff = Math.abs(rx - x);
    const yDiff = Math.abs(ry - y);
    const zDiff = Math.abs(rz - z);

    if (xDiff > yDiff && xDiff > zDiff) rx = -ry - rz;
    else if (yDiff > zDiff) ry = -rx - rz;
    else rz = -rx - ry;

    return [rx, ry, rz];
}

function pixelToCube(x, y) {
    const mouseX = x - ORIGIN_X;
    const mouseY = y - ORIGIN_Y;
    const q = (mouseX * (2/3)) / HEX_SIZE;
    const r = (-mouseX/3 + mouseY/Math.sqrt(3)) / HEX_SIZE;
    return cubeRound(q, -q - r, r);
}

function drawPiece(x, y, z, piece) {
    const center = cubeToPixel(x, y, z);
    ctx.fillStyle = piece.owner === "Red" ? "#e74c3c" : "#ecf0f1";
    
    switch(piece.type) {
        case 'Sentry':
            ctx.beginPath();
            ctx.arc(center.x, center.y, HEX_SIZE/3, 0, Math.PI*2);
            ctx.fill();
            break;
        case 'Shield':
            ctx.fillRect(center.x - HEX_SIZE/3, center.y - HEX_SIZE/3, HEX_SIZE*0.66, HEX_SIZE*0.66);
            break;
        case 'Striker':
            ctx.beginPath();
            ctx.moveTo(center.x + HEX_SIZE/2, center.y);
            ctx.lineTo(center.x, center.y + HEX_SIZE/2);
            ctx.lineTo(center.x - HEX_SIZE/2, center.y);
            ctx.lineTo(center.x, center.y - HEX_SIZE/2);
            ctx.closePath();
            ctx.fill();
            break;
        case 'Caster':
            ctx.beginPath();
            ctx.arc(center.x, center.y, HEX_SIZE/3, 0, Math.PI*2);
            ctx.fill();
            ctx.strokeStyle = "#f1c40f";
            ctx.lineWidth = 2;
            ctx.stroke();
            break;
    }
}

function drawBoard() {
    fetch('/get_board')
        .then(response => response.json())
        .then(data => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            data.tiles.forEach(hexStr => {
                const [x, y, z] = hexStr.split(',').map(Number);
                drawHex(x, y, z);
            });

            Object.entries(data.pieces).forEach(([coords, piece]) => {
                const [x, y, z] = coords.split(',').map(Number);
                drawPiece(x, y, z, piece);
            });
        });
}

canvas.addEventListener('click', async (e) => {
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const [q, r, s] = pixelToCube(x, y);
    
    if(selectedPiece) {
        const response = await fetch('/move', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                piece_type: selectedPiece.type,
                start_hex: selectedPiece.coords,
                target_hex: [q, r, s]
            })
        });
        const result = await response.json();
        if(result.success) drawBoard();
        selectedPiece = null;
    } else {
        const pieces = await fetch('/get_board').then(res => res.json());
        const coordStr = `${q},${r},${s}`;
        
        if(pieces.pieces[coordStr]) {
            selectedPiece = {
                coords: [q, r, s],
                type: pieces.pieces[coordStr].type
            };
        }
    }
});

drawBoard();
setInterval(drawBoard, 1000);