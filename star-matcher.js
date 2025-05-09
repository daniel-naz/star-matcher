function* combinationsOf4(arr) {
    const n = arr.length;
    for (let i = 0; i < n; i++) {
        for (let j = i + 1; j < n; j++) {
            for (let k = j + 1; k < n; k++) {
                for (let l = k + 1; l < n; l++) {
                    yield [arr[i], arr[j], arr[k], arr[l]]
                }
            }
        }
    }
}

function* combinationsOf2(arr) {
    const n = arr.length;
    for (let i = 0; i < n - 1; i++) {
        for (let j = i + 1; j < n; j++) {
            yield [arr[i], arr[j]]
        }
    }
}

function createGrid(size) {
    return Array.from({ length: size }, () =>
        Array.from({ length: size }, () =>
            [] 
        )
    );
}

function distance(p1, p2) {
    return Math.sqrt((p1.x - p2.x) * (p1.x - p2.x) + (p1.y - p2.y) * (p1.y - p2.y))
}

function angleBetweenLines(p0, p1, p2) {
    const v1x = p1.x - p0.x;
    const v1y = p1.y - p0.y;
    const v2x = p2.x - p1.x;
    const v2y = p2.y - p1.y;

    const dotProduct = v1x * v2x + v1y * v2y;

    const magnitudeV1 = Math.sqrt(v1x * v1x + v1y * v1y);
    const magnitudeV2 = Math.sqrt(v2x * v2x + v2y * v2y);


    const cosTheta = dotProduct / (magnitudeV1 * magnitudeV2);
    const clampedCosTheta = Math.min(Math.max(cosTheta, -1), 1);

    let angle = Math.acos(clampedCosTheta);

    if (angle > Math.PI) {
        angle = 2 * Math.PI - angle;
    }

    return angle;
}


function farthestAndOthers(...points) {
    let maxDist = -1
    let farthestPair = [undefined, undefined]

    for (const [p1, p2] of combinationsOf2(points)) {
        let d = distance(p1, p2)

        if (d > maxDist) {
            maxDist = d
            farthestPair = [p1, p2]
        }
    }

    let foundOther = false
    let other1 = undefined
    let other2 = undefined

    for (const p of points) {
        if (p != farthestPair[0] && p != farthestPair[1]) {
            if (!foundOther) {
                other1 = p
                foundOther = true
            }
            else {
                other2 = p
            }
        }
    }

    return [farthestPair[0], farthestPair[1], other1, other2, maxDist]
}

function constructFeature(...points) {
    let [f1, f2, o1, o2, maxdist] = farthestAndOthers(...points)

    if (f2[0] < f1[0]) [f1, f2] = [f2, f1]

    let d1o1 = distance(o1, f1)
    let d1o2 = distance(o2, f1)

    if (d1o2 < d1o1) {
        [o1, o2] = [o2, o1]
        [d1o1, d1o2] = [d1o2, d1o1]
    }

    let d2o1 = distance(o1, f2)
    let d2o2 = distance(o2, f2)

    let angle = angleBetweenLines(o1, f1, f2)

    if (angle < 0.1 || isNaN(angle)) return undefined

    return [f1, f2, maxdist, [d1o1, d2o1], [d1o2, d2o2], o1, o2, angle]
}

function areShapesSimilar(s1, s2, tol = 0.1) {
    const scale = s1[2] / s2[2]

    const [s1_d1o1, s1_d2o1] = s1[3]
    const [s1_d1o2, s1_d2o2] = s1[4]
    const [s2_d1o1, s2_d2o1] = s2[3]
    const [s2_d1o2, s2_d2o2] = s2[4]

    if (Math.abs(s1_d1o1 - s2_d1o1 * scale) > tol) return false
    if (Math.abs(s1_d2o1 - s2_d2o1 * scale) > tol) return false
    if (Math.abs(s1_d1o2 - s2_d1o2 * scale) > tol) return false
    if (Math.abs(s1_d2o2 - s2_d2o2 * scale) > tol) return false

    return [[s1[0], s1[1], s1[5], s1[6]], [s2[0], s2[1], s2[5], s2[6]]]
}

function matchStars(stars1, stars2, img1, img2, gridCells = 10, tol = 0.1) {    
    console.log("Creating grid");
    const grid1 = createGrid(gridCells)
    const grid2 = createGrid(gridCells)

    const [w1, h1] = [img1.width, img1.height]
    const [w2, h2] = [img2.width, img2.height]

    const [cellw1, cellh1] = [w1 / gridCells, h1 / gridCells]
    const [cellw2, cellh2] = [w2 / gridCells, h2 / gridCells]


    for (const s1 of stars1) {
        const [x, y] = [Math.floor(s1.x / cellw1), Math.floor(s1.y / cellh1)]
        grid1[y][x].push(s1)
    }

    for (const s2 of stars2) {
        const [x, y] = [Math.floor(s2.x / cellw2), Math.floor(s2.y / cellh2)]
        grid2[y][x].push(s2)
    }

    console.log("Creating features");
    const features1 = []
    const features2 = []
    
    for (let i = 0; i < gridCells; i++) {
        for (let j = 0; j < gridCells; j++) {

            const mini = Math.max(0, i - 1)
            const maxi = Math.min(gridCells, i + 2)

            const temparr1 = []
            const temparr2 = []

            for (let _i = mini; _i < maxi; _i++) {

                const minj = Math.max(0, j - 1)
                const maxj = Math.min(gridCells, j + 2)

                for (let _j = minj; _j < maxj; _j++) {
                    temparr1.push(...grid1[_i][_j])
                    temparr2.push(...grid2[_i][_j])
                }
            }

            for (const combo of combinationsOf4(temparr1)) {
                const feet = constructFeature(...combo)
                if (feet) features1.push(feet)
            }
            for (const combo of combinationsOf4(temparr2)) {
                const feet = constructFeature(...combo)
                if (feet) features2.push(feet)
            }
        }
    }
    console.log(`Added ${features1.length} to graph1 and ${features2.length} to graph2.`);

    console.log("Matching");
    const result = []

    var count = 0
    var last = 0
    for (const f1 of features1) {
        for (const f2 of features2) {

            count++
            if (Math.floor(count / (features1.length * features2.length) * 100) > last) {
                last = Math.floor(count / (features1.length * features2.length) * 100)
                console.log(`${last}%`);
            }

            if (areShapesSimilar(f1, f2, tol)) {
                result.push([f1, f2])
                break
            }
        }
    }

    console.log(`Found ${result.length} matches.`);
    return result
}

export default {
    matchStars
}