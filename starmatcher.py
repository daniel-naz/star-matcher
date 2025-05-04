import random
from star import Star
from linenode import LineNode
import cv2
import math
from graph_utils import min_connecting_distance

class StarMatcher: 

    def __init__(self, brightness_threshold=200, min_cluster_size=3, max_graph_dist=None):
        """Create a new star identification object.

        Args:
            brightness_threshold (int, optional): Minimum brightness to consider a pixel a star. Defaults to 200.
            min_cluster_size (int, optional): Minimum number of bright adjacent pixels needed to clasify them as a star. Defaults to 3.
        """
        
        self.brightness_threshold = brightness_threshold
        self.min_cluster = min_cluster_size
        self.max_graph_dist = max_graph_dist

    def build_graph(self, stars : list[Star]):
        """Construct a line graph connecting all the bright stars

        Args:
            stars (list[Star]): List of all the stars identified in the picture.
            max_dist (int, optional): The maximum distance where the stars will connect in the graph. Defaults to 500.
        """
        dist = self.max_graph_dist

        if not self.max_graph_dist:
            dist = min_connecting_distance(stars)

        print("dist = ", dist)

        lines : list[LineNode] = []

        # Create uniqe lines
        n = len(stars)
        for i in range(n):
            for j in range(i + 1, n):
                # Create the line
                templine = LineNode(stars[i], stars[j])
                
                # Make sure length is valid
                if templine.length > dist: continue
                
                lines.append(templine)
                stars[i].lines.append(templine)
                stars[j].lines.append(templine)

        # Create graph by connecting lines

        for s in stars:
            n = len(s.lines)
            for i in range(n):
                for j in range(i + 1, n):
                    angle, _ = LineNode.calc_inner_angle(s.lines[i], s.lines[j])
                    s.lines[i].add_child(s.lines[j], angle)
                    s.lines[j].add_child(s.lines[i], angle)

        return lines


    def detect_stars(self, img_path : str):
        """Detect starts inside of an image and return them in a list.

        Args:
            img_path (str): Image with stars.
        """

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise FileNotFoundError(f"Image not found: {img_path}")

        height, width = img.shape
        visited = [[False for _ in range(width)] for _ in range(height)]
        stars : list[Star] = []

        def get_pixel(x, y):
            return int(img[y, x])  # Note: img[y, x] is row-major

        def get_neighbors(x, y):
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        yield nx, ny

        def flood_fill(x, y):
            cluster = []
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if visited[cy][cx]:
                    continue
                visited[cy][cx] = True
                if get_pixel(cx, cy) >= self.brightness_threshold:
                    cluster.append((cx, cy))
                    stack.extend(get_neighbors(cx, cy))
            return cluster

        for y in range(height):
            for x in range(width):
                if not visited[y][x] and get_pixel(x, y) >= self.brightness_threshold:
                    cluster = flood_fill(x, y)
                    if len(cluster) >= self.min_cluster:
                        sx = sum(p[0] for p in cluster)
                        sy = sum(p[1] for p in cluster)
                        avg_x = sx / len(cluster)
                        avg_y = sy / len(cluster)
                        avg_brightness = sum(get_pixel(cx, cy) for cx, cy in cluster) / len(cluster)
                        max_r = max(math.hypot(cx - avg_x, cy - avg_y) for cx, cy in cluster)
                        stars.append(Star(avg_x, avg_y, int(avg_brightness), max_r))

        stars = [s for s in stars if s.r != 0]
        return stars

    def detect_matching_stars(self, image_path1 : str, image_path2 : str, min_matches=5, angle_offset=0.005, dist_offset=0.005, match_offset=None):
        """Find and match stars from 2 different images

        Returns:
            (list[tuple[Star, Star]]): List of matching stars. index 0 = image 1, index 1 = image 2.
        """
        stars1 = self.detect_stars(image_path1)
        stars2 = self.detect_stars(image_path2) 
        graph1 = self.build_graph(stars1)
        graph2 = self.build_graph(stars2)

        matching = StarMatcher.match_stars(stars1, stars2, graph1, graph2, cv2.imread(image_path1).shape[1], min_matches, angle_offset, dist_offset, match_offset)
        return matching

    @staticmethod 
    def match_stars(stars1 : list[Star], stars2 : list[Star], graph1 : list[LineNode], graph2 : list[LineNode], offset_width, min_matches=5, angle_offset=0.005, dist_offset=0.01, match_offset=None):
        pass