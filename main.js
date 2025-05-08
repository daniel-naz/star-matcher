import matcher from "./star-matcher.js"
import detector from "./star-detector.js"

const stars1 = [];
const stars2 = [];
var img1 = null;
var img2 = null;

function drawImageOnly(canvas, img) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (!img) return;
    ctx.drawImage(img, 0, 0);
}

async function loadImage(fileInput, canvas) {
    const file = fileInput.files[0];
    if (!file) return null;

    const img = new Image();
    img.src = URL.createObjectURL(file);
    await img.decode();

    canvas.width = img.width;
    canvas.height = img.height;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(img, 0, 0);

    return img
}

    function randomRGB() {
        const r = Math.floor(Math.random() * 256); // 0–255
        const g = Math.floor(Math.random() * 256);
        const b = Math.floor(Math.random() * 256);
        return `rgb(${r}, ${g}, ${b})`;
    }

function painPoints(p1, p2, ctx1, ctx2) {
    const color = randomRGB()

    ctx1.strokeStyle = color;
    ctx1.lineWidth = 1.5;
    ctx2.strokeStyle = color;
    ctx2.lineWidth = 1.5;

    ctx1.beginPath();
    ctx1.arc(p1.x, p1.y, 3, 0, 2 * Math.PI);
    ctx1.stroke();

    ctx2.beginPath();
    ctx2.arc(p2.x, p2.y, 3, 0, 2 * Math.PI);
    ctx2.stroke();
}

function drawLine(ctx, x1, y1, x2, y2, color = 'black', width = 1) {
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.stroke();
}

window.addEventListener('DOMContentLoaded', () => {
    const file1 = document.getElementById('file1');
    const file2 = document.getElementById('file2');
    const canvas1 = document.getElementById('canvas1');
    const canvas2 = document.getElementById('canvas2');
    const recalcBtn = document.getElementById('recalc');
    const matchBtn = document.getElementById('match');
    const thresholdslider = document.getElementById('threshold');
    const gridslider = document.getElementById('gridSize');
    const thresholddisplay = document.getElementById('thresholdValue');
    const griddisplay = document.getElementById('gridSizeValue');

    thresholdslider.addEventListener('input', () => {
        thresholddisplay.textContent = thresholdslider.value;
    });

    file1.addEventListener('change', async () => {
        img1 = await loadImage(file1, canvas1)
        detector.detectStars(canvas1, stars1)
    });

    file2.addEventListener('change', async () => {
        img2 = await loadImage(file2, canvas2)
        detector.detectStars(canvas2, stars2)
    });

    recalcBtn.addEventListener('click', () => {
        // clear and redraw images
        drawImageOnly(canvas1, img1);
        drawImageOnly(canvas2, img2);
        detector.detectStars(canvas1, stars1)
        detector.detectStars(canvas2, stars2)
    });

    gridslider.addEventListener('input', () => {
        griddisplay.textContent = gridslider.value;
    });

    matchBtn.addEventListener('click', () => {
        if (!img1 || !img2 || !stars1.length || !stars2.length) return;

        drawImageOnly(canvas1, img1);
        drawImageOnly(canvas2, img2);

        const matches = matcher.matchStars(stars1, stars2, img1, img2, 29, 0.245);

        const ctx1 = canvas1.getContext('2d');
        const ctx2 = canvas2.getContext('2d');

        for (const [s1, s2] of matches) {
            painPoints(s1[0], s2[0], ctx1, ctx2)
            painPoints(s1[1], s2[1], ctx1, ctx2)
            painPoints(s1[5], s2[5], ctx1, ctx2)
            painPoints(s1[6], s2[6], ctx1, ctx2)

            const c =  randomRGB()

            drawLine(ctx1, s1[0].x, s1[0].y, s1[1].x, s1[1].y, c, 1)
            drawLine(ctx1, s1[1].x, s1[1].y, s1[5].x, s1[5].y, c, 1)
            drawLine(ctx1, s1[5].x, s1[5].y, s1[6].x, s1[6].y, c, 1)
   
            drawLine(ctx2, s2[0].x, s2[0].y, s2[1].x, s2[1].y, c, 1)
            drawLine(ctx2, s2[1].x, s2[1].y, s2[5].x, s2[5].y, c, 1)
            drawLine(ctx2, s2[5].x, s2[5].y, s2[6].x, s2[6].y, c, 1)
        }
    });
});