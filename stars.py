import cv2
import numpy as np
from identifier import detect_stars

def connect_images(image1, image2, direction='horizontal'):
    """
    Connects two images either horizontally or vertically.

    Args:
    - image1 (numpy array): First image.
    - image2 (numpy array): Second image.
    - direction (str): 'horizontal' or 'vertical' (default is 'horizontal').

    Returns:
    - numpy array: The combined image.
    """

    image1 = cv2.imread(image1)
    image2 = cv2.imread(image2)

    # Ensure the images are of the same size in the concatenation axis
    if direction == 'horizontal':
        # Resize images to have the same height
        height = max(image1.shape[0], image2.shape[0])
        image1_resized = cv2.resize(image1, (image1.shape[1], height))
        image2_resized = cv2.resize(image2, (image2.shape[1], height))
        return np.hstack((image1_resized, image2_resized))  # Concatenate horizontally

    elif direction == 'vertical':
        # Resize images to have the same width
        width = max(image1.shape[1], image2.shape[1])
        image1_resized = cv2.resize(image1, (width, image1.shape[0]))
        image2_resized = cv2.resize(image2, (width, image2.shape[0]))
        return np.vstack((image1_resized, image2_resized))  # Concatenate vertically

    else:
        raise ValueError("Direction must be 'horizontal' or 'vertical'")

stars = detect_stars("fr1.jpg",2,8,0.1)

print("circling")
img = cv2.imread("fr1.jpg")

for x, y, r, b in stars:
    cv2.circle(img, (int(x), int(y)), int(r), (0, 0, 255), 3)

cv2.imwrite("temp.jpg", img)


img = connect_images("fr1.jpg", "temp.jpg")
cv2.imwrite("output.jpg", img)

