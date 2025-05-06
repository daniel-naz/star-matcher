import numpy as np
from scipy.ndimage import gaussian_laplace, label, center_of_mass
from skimage import io
from skimage.color import rgb2gray
from skimage import feature


def detect_stars(image, min_sigma=2, max_sigma=8, threshold=0.02):
    image = io.imread(image).astype(np.float32)/255.0

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

    # Detect blobs using Laplacian of Gaussian :
    # this is used for edge detection so we can check for edges of 
    # the stars. the min/max sigma represent the ~the min/max size of the stars detected.
    blobs = feature.blob_log(image_gray, min_sigma=min_sigma,
                             max_sigma=max_sigma, num_sigma=10,
                             threshold=threshold)

    # Compute radius :
    # the 3rd colum (index 2) stores the sigma data (~the star size)
    # we can convert it into a radius by multiplying be sqrt(2)
    # source : https://stackoverflow.com/questions/51382850/finding-the-average-pixel-values-of-a-list-of-blobs-identified-by-scikit-images
    blobs[:, 2] = blobs[:, 2] * np.sqrt(2)

    # Prepare list to hold blob information
    blob_info = []
    
    rows, cols = image_gray.shape
    row_indices, col_indices = np.ogrid[:rows, :cols]

    for y, x, r in blobs:
        # Create a boolean mask to keep trak for the indexes of the pixels  
        # in the current blob (based on the circle formula (y - y1)^2 + (x - x1)^2 <= r^2)
        mask = (row_indices - y)**2 + (col_indices - x)**2 <= r**2

        # Calculate mean brightness within the mask
        brightness = image_gray[mask].mean()

        # Append blob information: (x, y, radius, brightness)
        blob_info.append((x, y, r, brightness))

    # Return only the first two columns (e.g., x and y coordinates)
    return blob_info
