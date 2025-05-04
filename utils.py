from itertools import combinations
import math
import random
import cv2
import numpy as np
from starmatcher import StarMatcher, LineNode

import cv2

def rotate_image_180(image_path : str, output_path="rotated180.jpg"):
    """ Rotates the input image by 180 degrees. """
    img = cv2.imread(image_path)
    img = cv2.rotate(img, cv2.ROTATE_180)
    cv2.imwrite(output_path, img)


def connect_images(*image_paths, output_path="connected.jpg"):
    """
    Load multiple images and connect them horizontally into one image.
    
    Arguments:
        *image_paths: paths to images.
    
    Returns:
        A single combined image (numpy array).
    """
    images = []

    for path in image_paths:
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Cannot load image: {path}")
        images.append(img)

    max_height = max(img.shape[0] for img in images)

    resized_images = []
    for img in images:
        h, w = img.shape[:2]
        resized_img = np.full((max_height, w, 3), 255, dtype=np.uint8)
        resized_img[:h, :] = img
        resized_images.append(resized_img)

    connected_img = cv2.hconcat(resized_images)

    cv2.imwrite(output_path, connected_img)
    print(f"Saved output to: {output_path}")

    return resized_images


def draw_stars(image_path : str, matcher : StarMatcher, output_path="output_with_stars.jpg",
                radiusmul=3, color=(0, 0, 255), thickness=2):
    """Detect stars inside of an image then draw circles around the stars in a copied image.

    Args:
        image_path (str): Path to original image.
        matcher (StarMatcher): Detector object used for calculations.
        output_path (str, optional): Output image path. Defaults to "output_with_stars.jpg".
        radiusmul (int, optional): Original star radius multiplier. Defaults to 3.
        color (tuple, optional): Color of circle. Defaults to red (0, 0, 255).
        thickness (int, optional): Thickness of circle. Defaults to 2.

    Raises:
        FileNotFoundError: When the original file can't be found.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    stars = matcher.detect_stars(image_path)

    for star in stars:
        cv2.circle(img, star.iposition, int(star.r) * radiusmul, color, thickness)  # Red circle, thin line

    cv2.imwrite(output_path, img)
    print(f"Saved output to: {output_path}")


def draw_constellations(image_path : str, matcher : StarMatcher, output_path="output_with_constellations.jpg",
                        color=(0, 0, 255), thickness=2):
    """Draw lines between the stars to create makeshift "constellations".

    Args:
        image_path (str): Path to original image.
        matcher (StarMatcher): Detector object used for calculations.
        output_path (str, optional): Output image path. Defaults to "output_with_constellations.jpg".
        color (tuple, optional): Color of line. Defaults to (0, 0, 255).
        thickness (int, optional): Thickness of line. Defaults to 2.

    Raises:
        FileNotFoundError: _description_
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    lines = matcher.build_graph(matcher.detect_stars(image_path))

    for line in lines:
        cv2.line(img, line.star1.iposition, line.star2.iposition, color, thickness)

    cv2.imwrite(output_path, img)
    print(f"Saved output to: {output_path}")


def draw_graph(image_path : str, matcher : StarMatcher, output_path="output_with_graph.jpg", line_color=(0, 0, 255), angle_color=(255, 255, 255)):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    lines = matcher.build_graph(matcher.detect_stars(image_path))

    for line in lines:
        cv2.line(img, line.star1.iposition, line.star2.iposition, line_color, 2)
        
        for child, angle in line.children:
            draw_inner_angle(img, line, child, color=angle_color)

    cv2.imwrite(output_path, img)
    print(f"Saved output to: {output_path}")


def random_color():
    """Generate a random color in BGR format (for OpenCV)."""
    return (random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255))

def draw_inner_angle(img, line1, line2, radius=30, color=(0, 0, 255), thickness=2):
    """Draw the inner angle at point p1 formed by (p0 -> p1 -> p2)."""
    angle, start_angle = LineNode.calc_inner_angle(line1, line2)

    end_angle = start_angle + angle

    center = LineNode.get_common_star(line1, line2)
    radius = int(radius + radius * (end_angle - start_angle) / 360)

    # Draw the arc
    cv2.ellipse(img, center.iposition, (radius, radius), start_angle, 0, angle, color, thickness)
