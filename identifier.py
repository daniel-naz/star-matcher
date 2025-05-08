from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations
import math
import cv2
import numpy as np
from scipy.ndimage import gaussian_laplace, label, center_of_mass
from skimage import io
from skimage.color import rgb2gray
from skimage import feature
from scipy.spatial.distance import cdist
from PIL import Image, ImageDraw
import concurrent.futures

def remove_lowest_brightness(arr : list, removed_threshold):
    return [x for x in arr if x[3] > removed_threshold]


count = 0

def match_one_feature(args): 
    global count

    count += 1
    if count % 500 == 0: print (count)

    s1, features2, tol = args

    for s2 in features2:
        res = are_shapes_similar(s1, s2, tol)
        if res: return res
    return None


def stars_from_cells(grid, cx, cy):
    COUNT = 1
    result = []

    for y in range(max(0, cy - COUNT), min(cy + 1 + COUNT, len(grid))):
        for x in range(max(0, cx - COUNT), min(cx + 1 + COUNT, len(grid[1]))):
            result.extend(grid[y][x])

    return result


def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def farthest_and_others(points):
    max_dist = -1
    farthest_pair = (None, None)

    for a, b in combinations(points, 2):
        d = distance(a, b)
        if d > max_dist:
            max_dist = d
            farthest_pair = (a, b)
    
    found_other = False

    for a in points:
        if a != farthest_pair[0] and a != farthest_pair[1]:
            if not found_other:
                other1 = a
                found_other = True
            else:
                other2 = a

    return farthest_pair[0], farthest_pair[1], other1, other2, max_dist


def are_shapes_similar(s1, s2, tol=0.5):
    def check_order(d1o1, d2o1, d1o2, d2o2): 
        scale = s1[2] / s2[2]

        (s1_d1o1, s1_d2o1), (s1_d1o2, s1_d2o2) = d1o1, d2o1
        (s2_d1o1, s2_d2o1), (s2_d1o2, s2_d2o2) = d1o2, d2o2

        if abs(s1_d1o1 - s2_d1o1 * scale) > tol: return False
        if abs(s1_d2o1 - s2_d2o1 * scale) > tol: return False
        if abs(s1_d1o2 - s2_d1o2 * scale) > tol: return False
        if abs(s1_d2o2 - s2_d2o2 * scale) > tol: return False
        return True

    # original match : f1, f2, o1, o2 => f1, f2, o1, o2
    if check_order(s1[3], s1[4], s2[3], s2[4]): 
        return (s1[0], s1[1], s1[5], s1[6]), (s2[0], s2[1], s2[5], s2[6])

    return False


def construct_feature(points):
    (f1, f2, o1, o2, maxdist) = farthest_and_others(points)
    
    # define f1 by the x axis:
    if f2[0] < f1[0]:
        f1, f2 = f2, f1

    d1o1 = distance(o1, f1)
    d1o2 = distance(o2, f1)    

    # define o1 as the closest to f1
    if d1o2 < d1o1:
        o1, o2 = o2, o1
        d1o1, d1o2 = d1o2, d1o1

    d2o1 = distance(o1, f2)
    d2o2 = distance(o2, f2)

    return (f1, f2, maxdist, (d1o1, d2o1), (d1o2, d2o2), o1, o2)


def image_to_grayscale(image):

    # Convert RGBA to RGB if necessary :
    # check if there are 3 dimantions (width, height, channels) and check if it
    # it has 4 channels (RGBA), convert to 3 channels by taking only the first 3.
    if image.ndim == 3 and image.shape[-1] == 4:
        image = image[..., :3]

    # Convert RGB to grayscale : 
    # check if it has 3 dimantions (width, height, channels) and convert
    # to 2 channels (width, height) (grayscale)
    if image.ndim == 3:
        image_gray = rgb2gray(image)

    else:
        image_gray = image

    return image_gray


def detect_stars(image, min_sigma=2, max_sigma=8, threshold=0.02, prints=True):
    if isinstance(image, str):
        if prints: print(f"""Staring locating stars. Reading "{image}"...""")
        image = io.imread(image).astype(np.float32) / 255.0

    if prints: print(f"""Converting image to grayscale...""")
    image_gray = image_to_grayscale(image)

    if prints: print(f"""Locating stars...""")
    # Detect blobs using Laplacian of Gaussian :
    # this is used for edge detection so we can check for edges of 
    # the stars. the min/max sigma represent the ~the min/max size of the stars detected.
    blobs = feature.blob_log(image_gray, min_sigma=min_sigma,
                             max_sigma=max_sigma, num_sigma=10,
                             threshold=threshold)

    if prints: print(f"""Computing radii...""")
    # Compute radius :
    # the 3rd colum (index 2) stores the sigma data (~the star size)
    # we can convert it into a radius by multiplying be sqrt(2)
    # source : https://stackoverflow.com/questions/51382850/finding-the-average-pixel-values-of-a-list-of-blobs-identified-by-scikit-images
    blobs[:, 2] = blobs[:, 2] * np.sqrt(2)

    # Prepare list to hold blob information
    blob_info = []
    
    rows, cols = image_gray.shape
    row_indices, col_indices = np.ogrid[:rows, :cols]

    if prints: print(f"""Computing brightness...""")
    for y, x, r in blobs:
        # Create a boolean mask to keep trak for the indexes of the pixels  
        # in the current blob (based on the circle formula (y - y1)^2 + (x - x1)^2 <= r^2)
        mask = (row_indices - y)**2 + (col_indices - x)**2 <= r**2

        # Calculate mean brightness within the mask
        brightness = image_gray[mask].mean()

        # Append blob information: (x, y, radius, brightness)
        blob_info.append((x, y, r, brightness))

    if prints: print(f"""Done ! found {len(blob_info)} stars.""")
    # Return only the first two columns (e.g., x and y coordinates)
    return blob_info


def match_stars(image1, image2, min_sigma=2, max_sigma=8, threshold=0.02, grid_cells=45, removed_threshold=0.3, tol=0.2, prints=True):

    if prints: print("Starting matching.")

    if isinstance(image1, str):     
        if prints: print(f"""Reading "{image1}"...""")
        image1 = io.imread(image1).astype(np.float32) / 255.0

    if isinstance(image2, str):     
        if prints: print(f"""Reading "{image2}"...""")
        image2 = io.imread(image2).astype(np.float32) / 255.0


    if prints: print(f"""Locating stars in images...""")
    stars1 = detect_stars(image1, min_sigma, max_sigma, threshold, prints)
    stars2 = detect_stars(image2, min_sigma, max_sigma, threshold, prints)

    if prints: print(f"""Remove dim stars...""")
    plen1, plen2 = len(stars1), len(stars2)
    stars1 = remove_lowest_brightness(stars1, removed_threshold)
    stars2 = remove_lowest_brightness(stars2, removed_threshold)

    if prints: print(f"""Removed {plen1 - len(stars1)} stars form image1 and {plen2 - len(stars2)} from image 2.""")

    if prints: print(f"""Placing stars into grids...""")
    grid1 = [[[] for _ in range(grid_cells)] for _ in range(grid_cells)]
    grid2 = [[[] for _ in range(grid_cells)] for _ in range(grid_cells)]

    h1, w1 = image1.shape[0], image1.shape[1]
    h2, w2 = image2.shape[0], image2.shape[1]
    dt_h1, dt_w1 = h1 / grid_cells, w1 / grid_cells
    dt_h2, dt_w2 = h2 / grid_cells, w2 / grid_cells

    for s1 in stars1:
        x, y = int(s1[0] / dt_w1), int(s1[1] / dt_h1)
        grid1[y][x].append(s1)

    for s2 in stars2:
        x, y = int(s2[0] / dt_w2), int(s2[1] / dt_h2)
        grid2[y][x].append(s2)


    if prints: print(f"""Building geometic features...""")
    features1 = []
    features2 = []

    for y in range(grid_cells):
        for x in range(grid_cells):
            for shape in combinations(stars_from_cells(grid1, x, y), 4):
                features1.append(construct_feature(shape))
            for shape in combinations(stars_from_cells(grid2, x, y), 4):
                features2.append(construct_feature(shape))

        
    if prints: print(f"""Built {len(features1)} shapes from image1 and {len(features2)} from image2.""")
    if prints: print(f"""Comparing shapes in images...""")

    def parallel_match(features1, features2):
        with ProcessPoolExecutor() as executor:
            # args_list = [(x, features2, tol) for x in features1]
            result = [] 

            futures = [executor.submit(match_one_feature, s1, features2, tol) for s1 in features1]
               
            for i, future in enumerate(as_completed(futures)):
                res = future.result()
                if res: result.append(res) 

        return result
    
    return parallel_match(features1, features2)


    