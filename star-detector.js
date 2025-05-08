function detectStars(canvas, storageArray) {
    const ctx = canvas.getContext('2d');

    const { width, height } = canvas;
    const imageData = ctx.getImageData(0, 0, width, height);
    const data = imageData.data;

    const threshold = parseInt(document.getElementById('threshold').value, 10);
    const visited = new Set();
    const stars = [];

    function getBrightness(r, g, b) {
        return 0.299 * r + 0.587 * g + 0.114 * b;
    }

    function floodFill(x, y) {
        const queue = [[x, y]];
        const pixels = [];
        let totalBrightness = 0;

        while (queue.length) {
            const [cx, cy] = queue.pop();
            const key = `${cx},${cy}`;
            if (visited.has(key) || cx < 0 || cy < 0 || cx >= width || cy >= height) continue;

            const idx = (cy * width + cx) * 4;
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            const brightness = getBrightness(r, g, b);
            if (brightness < threshold) continue;

            visited.add(key);
            pixels.push([cx, cy]);
            totalBrightness += brightness;

            queue.push([cx + 1, cy], [cx - 1, cy], [cx, cy + 1], [cx, cy - 1]);
        }

        if (pixels.length < 3) return null;

        const sumX = pixels.reduce((sum, p) => sum + p[0], 0);
        const sumY = pixels.reduce((sum, p) => sum + p[1], 0);
        const centerX = sumX / pixels.length;
        const centerY = sumY / pixels.length;
        const radius = Math.sqrt(pixels.length / Math.PI);
        const avgBrightness = totalBrightness / pixels.length;

        return { x: centerX, y: centerY, r: radius, b: avgBrightness };
    }

    for (let y = 0; y < height; y++) {
        for (let x = 0; x < width; x++) {
            const idx = (y * width + x) * 4;
            const r = data[idx], g = data[idx + 1], b = data[idx + 2];
            if (getBrightness(r, g, b) > threshold && !visited.has(`${x},${y}`)) {
                const star = floodFill(x, y);
                if (star) stars.push(star);
            }
        }
    }

    ctx.strokeStyle = 'lime';
    ctx.lineWidth = 1.5;
    stars.forEach(star => {
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.r + 2, 0, 2 * Math.PI);
        ctx.stroke();
    });

    storageArray.length = 0;
    storageArray.push(...stars);
}

export default {
    detectStars
}