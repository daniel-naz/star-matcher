from star import Star
from linenode import LineNode
import cv2
import math

class StarMatcher: 

    def __init__(self, brightness_threshold=200, min_cluster_size=3):
        """Create a new star identification object.

        Args:
            brightness_threshold (int, optional): Minimum brightness to consider a pixel a star. Defaults to 200.
            min_cluster_size (int, optional): Minimum number of bright adjacent pixels needed to clasify them as a star. Defaults to 3.
        """
        
        self.brightness_threshold = brightness_threshold
        self.min_cluster = min_cluster_size

    def build_graph(self, stars : list[Star], max_dist=800):
        """Construct a line graph connecting all the bright stars

        Args:
            stars (list[Star]): List of all the stars identified in the picture.
            max_dist (int, optional): The maximum distance where the stars will connect in the graph. Defaults to 500.
        """
        lines : list[LineNode] = []

        # Create uniqe lines
        for star1 in stars:
            for star2 in stars:
                # Make sure the line isn't of length 0
                if star1 == star2: continue

                # Create the line
                templine = LineNode(star1, star2)
                
                # Make sure length is valid
                if templine.length > max_dist: continue

                # Make sure the line wasn't already added
                flag = True
                for line in lines:
                    if templine == line:
                        flag = False
                        break
                
                if flag: lines.append(templine)

        # Create graph by connecting lines
        for line1 in lines:
            for line2 in lines:
                res = line1.add_child(line2)

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
                        stars.append(Star(int(avg_x), int(avg_y), int(avg_brightness), max_r))

        stars = [s for s in stars if s.r != 0]
        return stars

    def detect_matching_stars(self, image_path1 : str, image_path2 : str):
        """Find and match stars from 2 different images

        Returns:
            (list[tuple[Star, Star]]): List of matching stars. index 0 = image 1, index 1 = image 2.
        """
        graph1 = self.build_graph(self.detect_stars(image_path1))
        graph2 = self.build_graph(self.detect_stars(image_path2))

        matching = StarMatcher.match_stars(graph1, graph2)
        return matching

    @staticmethod 
    def match_stars(graph1 : list[LineNode], graph2 : list[LineNode], min_matches=5, angle_offset=0.01, dist_offset=0.05):
        possible_matches : list[tuple[
                LineNode,
                LineNode,
                list[tuple[LineNode, LineNode, int, int]]
            ]] = []

        angleoffset = 360 * angle_offset

        def childrenSort(graph : list["LineNode"]): 
            graph.sort(key=lambda line: len(line.children), reverse=True)

        childrenSort(graph1)
        childrenSort(graph2)

        def test_lines(line1 : LineNode, line2 : LineNode): 
            temp_matches = []
            used_indexes1 = []
            used_indexes2 = []

            for i, child1 in enumerate(line1.children):
                childline1, angle1 = child1
                for j, child2 in enumerate(line2.children):
                    childline2, angle2 = child2
                    if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
                        temp_matches.append((childline1, childline2, i, j))
                        used_indexes1.append(i)
                        used_indexes2.append(j)

            if len(temp_matches) >= min_matches:
                possible_matches.append((line1, line2, temp_matches))
                return True
            return False

        # Assume image was scaled proportionally - Compare angles only
        for line1 in graph1:
            if len(line1.children) < 2: continue
            for line2 in graph2:
                if len(line2.children) < 2: continue
                result = test_lines(line1, line2)
        
        if len(possible_matches) == 0: return []
        
        possible_matches.sort(key=lambda obj: len(obj[2]), reverse=True)

        # Test for distances
        def test_lengths():
            for line1, line2, matches in possible_matches:
                for child1, child2, i1, j1 in matches:
                    assumed_zoom = child1.length / child2.length

                    found_match = True
                    for test1, test2, i2, j2 in matches:
                        if i1 == i2 and j1 == j2: continue
                    
                        if abs((test1.length / test2.length) / assumed_zoom - 1) > dist_offset:
                            found_match = False
                            break
                
                    if found_match:
                        return (line1, line2, matches)
                    
        correct_guess = test_lengths()

        if correct_guess == None: return []

        # find matching stars in the correct guess
        s1s1_match = True
        s1s1_count = 0
        
        line1, line2, matches = correct_guess
        for l1, l2, i, j in matches: 
            if line1.children1.count(l1) != 0 and line2.children2.count(l2) != 0:
                s1s1_count += 1
        
        if not s1s1_count >= len(matches) // 2: s1s1_match = False

        p1, p2 = line1.star1.iposition, line1.star2.iposition
        p3, p4 = line2.star1.iposition, line2.star2.iposition
        if not s1s1_match: p3, p4 = p4, p3

        transform = transform_between_lines(p1, p2, p3, p4)

        print("transform = ", transform)

        img = cv2.imread("connected.jpg")
        height, width = img.shape[:2]

        temppos1 = correct_guess[1].star1.iposition
        temppos2 = correct_guess[1].star2.iposition

        cv2.line(img, correct_guess[0].star1.iposition, (temppos1[0] + int(width / 2), temppos1[1]), (255, 255, 255))
        cv2.line(img, correct_guess[0].star2.iposition, (temppos2[0] + int(width / 2), temppos2[1]), (255, 255, 255))
        cv2.imwrite("temp.jpg", img)

def distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def angle_between(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    det = v1[0]*v2[1] - v1[1]*v2[0]
    return math.atan2(det, dot)

def transform_between_lines(p1, p2, p3, p4):
    # Vectors
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p4[0] - p3[0], p4[1] - p3[1])

    # Scale (zoom)
    len1 = distance(p1, p2)
    len2 = distance(p3, p4)
    scale = len2 / len1 if len1 != 0 else 0

    # Rotation
    angle = angle_between(v1, v2)

    # Apply rotation and scaling to p1
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    sx, sy = p1[0] * scale, p1[1] * scale
    rx = cos_a * sx - sin_a * sy
    ry = sin_a * sx + cos_a * sy

    # Translation
    tx = p3[0] - rx
    ty = p3[1] - ry

    return {
        'scale': scale,
        'rotation_radians': angle,
        'rotation_degrees': math.degrees(angle),
        'translation': (tx, ty)
    }
