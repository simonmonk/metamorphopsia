// File: /metamorphopsia-html5/metamorphopsia-html5/src/app.js

const numLines = 21;
const dx = 30; // pixels
const width = (numLines - 1) * dx; // pixels
const midX = Math.floor(numLines / 2) * dx;
const dotR = dx / 10; // pixels
let bumpR = 4 * dx;
let date = new Date().toISOString().split('T')[0];
let titleBase = "Metamorphopsia Measurement Tool";

let selectedXLineNum = null;
let selectedYLineNum = null;

const hLines = Array.from({ length: numLines }, () => ({ offset: 0, value: 0 }));
const vLines = Array.from({ length: numLines }, () => ({ offset: 0, value: 0 }));

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = width;
canvas.height = width;

function setWindowTitle() {
    document.title = `${titleBase} (${date})`;
}

function reset() {
    for (let i = 0; i < numLines; i++) {
        hLines[i] = { offset: 0, value: 0 };
        vLines[i] = { offset: 0, value: 0 };
    }
    drawLines();
}

document.getElementById('saveButton').addEventListener('click', () => {
    const data = {
        bumpR,
        hLines,
        vLines,
        date
    };
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = `metamorphopsia_${date}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
});

document.getElementById('openButton').addEventListener('click', () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json,application/json';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                if (typeof data.bumpR === 'number') bumpR = data.bumpR;
                if (Array.isArray(data.hLines)) {
                    for (let i = 0; i < numLines; i++) {
                        hLines[i] = data.hLines[i] || { offset: 0, value: 0 };
                    }
                }
                if (Array.isArray(data.vLines)) {
                    for (let i = 0; i < numLines; i++) {
                        vLines[i] = data.vLines[i] || { offset: 0, value: 0 };
                    }
                }
                // Update slider to match loaded bumpR
                bumpWidthSlider.value = bumpR;
                drawLines();
            } catch (err) {
                alert('Invalid file format.');
            }
        };
        reader.readAsText(file);
    };
    input.click();
});

document.getElementById('exportButton').addEventListener('click', () => {
    // Convert canvas to data URL (PNG)
    const dataURL = canvas.toDataURL('image/png');
    // Create a temporary link to trigger download
    const a = document.createElement('a');
    a.href = dataURL;
    a.download = `metamorphopsia_${date}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
});

function drawLines() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let lineNum = 0; lineNum < numLines - 1; lineNum++) {
        drawHLine(lineNum);
        drawVLine(lineNum);
    }
    drawDot();
}

function drawDot() {
    const crossingX = midX;
    const crossingY = midX;
    ctx.beginPath();
    ctx.arc(crossingX, crossingY, dotR, 0, Math.PI * 2);
    ctx.fillStyle = "red";
    ctx.fill();
}

function drawHLine(lineNum) {
    const y = lineNum * dx;
    const line = hLines[lineNum];
    const distortion0x = midX + line.offset - bumpR;
    const distortion1x = midX + line.offset;
    const distortion2x = midX + line.offset + bumpR;
    const distortion_y = y + line.value;

    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(distortion0x, y);
    ctx.quadraticCurveTo(distortion1x, distortion_y, distortion2x, y);
    ctx.lineTo(width - 1, y);
    ctx.strokeStyle = selectedXLineNum === lineNum ? 'blue' : 'black';
    ctx.stroke();
}

function drawVLine(lineNum) {
    const x = lineNum * dx;
    const line = vLines[lineNum];
    const distortion0y = midX + line.offset - bumpR;
    const distortion1y = midX + line.offset;
    const distortion2y = midX + line.offset + bumpR;
    const distortion_x = x + line.value;

    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, distortion0y);
    ctx.quadraticCurveTo(distortion_x, distortion1y, x, distortion2y);
    ctx.lineTo(x, width - 1);
    ctx.strokeStyle = selectedYLineNum === lineNum ? 'blue' : 'black';
    ctx.stroke();
}

let dragging = false;

canvas.addEventListener('mousedown', (event) => {
    const x = event.offsetX;
    const y = event.offsetY;
    dragging = true;
    if (document.querySelector('input[name="axis"]:checked').value === 'x') {
        selectedXLineNum = Math.round(y / dx);
        selectedYLineNum = null;
    } else {
        selectedYLineNum = Math.round(x / dx);
        selectedXLineNum = null;
    }
});

canvas.addEventListener('mousemove', (event) => {
    if (!dragging) return;
    const x = event.offsetX;
    const y = event.offsetY;
    if (document.querySelector('input[name="axis"]:checked').value === 'x' && selectedXLineNum !== null) {
        const selectedLine = hLines[selectedXLineNum];
        selectedLine.offset = x - midX;
        selectedLine.value = y - (selectedXLineNum * dx);
    } else if (selectedYLineNum !== null) {
        const selectedLine = vLines[selectedYLineNum];
        selectedLine.offset = y - midX;
        selectedLine.value = x - (selectedYLineNum * dx);
    }
    drawLines();
});

canvas.addEventListener('mouseup', () => {
    dragging = false;
    selectedXLineNum = null;
    selectedYLineNum = null;
});

canvas.addEventListener('mouseleave', () => {
    dragging = false;
    selectedXLineNum = null;
    selectedYLineNum = null;
});

const bumpWidthSlider = document.getElementById('bumpWidth');
bumpWidthSlider.addEventListener('input', (event) => {
    bumpR = parseInt(event.target.value, 10);
    drawLines();
});

document.getElementById('resetButton').addEventListener('click', reset);
setWindowTitle();
drawLines();