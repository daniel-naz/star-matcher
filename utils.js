
function calculateAverageBrightness(imageData) {
    const data = imageData.data;
    const length = data.length;
    let totalBrightness = 0;
    const numPixels = length / 4;

    for (let i = 0; i < length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];
        
        const brightness = 0.299 * r + 0.587 * g + 0.114 * b;
        totalBrightness += brightness;
    }

    return totalBrightness / numPixels;
}

export default {
    calculateAverageBrightness
}