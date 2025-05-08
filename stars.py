import cv2
import numpy as np
from identifier import detect_stars, match_stars, construct_feature, are_shapes_similar, remove_lowest_brightness
import random

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


def draw_grid(image, x, color=(0, 255, 0), thickness=1):
    h, w = image.shape[:2]
    dx = w // x
    dy = h // x

    # Draw vertical lines
    for i in range(1, x):
        cv2.line(image, (i * dx, 0), (i * dx, h), color, thickness)

    # Draw horizontal lines
    for i in range(1, x):
        cv2.line(image, (0, i * dy), (w, i * dy), color, thickness)

    return image

image1 = cv2.imread("ST_db1.png")
image2 = cv2.imread("ST_db2.png")

# clone1 = image1.copy()
# for x in remove_lowest_brightness(detect_stars(image1), 0.0):
#     cv2.circle(clone1, (int(x[0]), int(x[1])), int(x[2]) * 3, (0, 0, 255))

# clone2 = image2.copy()
# for x in remove_lowest_brightness(detect_stars(image2), 0.0):
#     cv2.circle(clone2, (int(x[0]), int(x[1])), int(x[2]) * 3, (0, 0, 255))

# draw_grid(clone1, 40, (0, 0, 255))
# draw_grid(clone2, 40, (0, 0, 255))

# img = connect_images(clone1, clone2)
# cv2.imwrite("temp.jpg", img)

# # cv2.imwrite("stars1.jpg", clone1)
# # cv2.imwrite("stars2.jpg", clone2)

def color_circles(s1, s2):
    x1, y1, r1, b1 = s1 
    x2, y2, r2, b2 = s2

    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    cv2.circle(image1, (int(x1), int(y1)), int(r1) * 3, color)
    cv2.circle(image2, (int(x2), int(y2)), int(r2) * 3, color)

def main():    
    matches = match_stars("ST_db1.png", "ST_db2.png", threshold=0.015, grid_cells=40, removed_threshold=0, tol=0.2)

    print(matches)

    for s1, s2 in matches:
        color_circles(s1[0], s2[0])
        color_circles(s1[1], s2[1])
        color_circles(s1[2], s2[2])
        color_circles(s1[3], s2[3])

    img = connect_images(image1, image2)

    cv2.imwrite("output.jpg", img)


if  __name__ == "__main__":
    main()