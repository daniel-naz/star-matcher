import random
from star import Star
from linenode import LineNode
import cv2
import math

class StarMatcher: 

    def __init__(self, brightness_threshold=200, min_cluster_size=3, max_graph_dist=800):
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
        lines : list[LineNode] = []

        # Create uniqe lines
        n = len(stars)
        for i in range(n):
            for j in range(i + 1, n):
                # Create the line
                templine = LineNode(stars[i], stars[j])
                
                # Make sure length is valid
                if templine.length > self.max_graph_dist: continue
                
                lines.append(templine)
                stars[i].lines.append(templine)
                stars[j].lines.append(templine)

        # Create graph by connecting lines
        for s in stars:
            n = len(s.lines)

            for i in range(n):
                for j in range(i + 1, n):
                    if i == j: continue
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

    def detect_matching_stars(self, image_path1 : str, image_path2 : str, min_matches=5, angle_offset=0.01, dist_offset=0.05, match_offset=None):
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
    def match_stars(stars1 : list[Star], stars2 : list[Star], graph1 : list[LineNode], graph2 : list[LineNode], offset_width, min_matches=5, angle_offset=0.000005, dist_offset=0.0001, match_offset=None):
        possible_matches : list[tuple[
                LineNode,
                LineNode,
                list[tuple[LineNode, LineNode, int, int]]
            ]] = []

        angleoffset = 360 * angle_offset

        if match_offset == None:
            match_offset = 100000

            for s1 in stars2: 
                for s2 in stars2:       
                    if s1 == s2: continue
                    match_offset = min(match_offset, distance(s1.position, s2.position)) 
            match_offset /= 2

        def childrenSort(graph : list["LineNode"]): 
            graph.sort(key=lambda line: len(line.children), reverse=True)

        childrenSort(graph1)
        childrenSort(graph2)

        def test_lines(line1 : LineNode, line2 : LineNode): 
            temp_matches = []
            used_indexes1 = []
            used_indexes2 = []

            first = True
            assumed_zoom = 1

            for i, child1 in enumerate(line1.children):
                childline1, angle1 = child1
                for j, child2 in enumerate(line2.children):
                    childline2, angle2 = child2

                    if first:
                        if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
                            temp_matches.append((childline1, childline2))
                            used_indexes1.append(i)
                            used_indexes2.append(j)
                            assumed_zoom = childline1.length / childline2.length
                            first = False
                            
                    else:
                        if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
                            if abs((childline1.length / childline2.length) / assumed_zoom - 1) > dist_offset:
                                temp_matches.append((childline1, childline2))
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

        correct_guess = possible_matches[0]

        # find matching stars in the correct guess
        correct_guess = possible_matches[0]
        
        line1, line2, matches = correct_guess

        p1, p2 = line1.star1.position, line1.star2.position
        p3, p4 = line2.star1.position, line2.star2.position

        child1, child2 = matches[0]
        is_p1 = line1.children1.count(child1) > 0
        is_p3 = line2.children1.count(child2) > 0

        if (is_p1 or not is_p3) or (not is_p1 or is_p3):
            p3, p4 = p4, p3 

        transform = transform_between_lines(p1, p2, p3, p4)

        print("transform = ", transform)

        # FINALLY! match the stars
        img = cv2.imread("temp.jpg")

        result : list[tuple[Star, Star]]= []        
        transformed_positions = []
        for star1 in stars1:
            transformed_positions.append(apply_transform(transform, star1.position))
        
        for l1, l2, m in possible_matches:
            color = (255, 0, 0)
            
            cv2.line(img, l1.star1.iposition, l1.star2.iposition, color, 2)
            cv2.line(img, (l2.star1.iposition[0] + offset_width, l2.star1.iposition[1]), (l2.star2.iposition[0] + offset_width, l2.star2.iposition[1]), color, 2)

        for i, star2 in enumerate(stars2):
            for j, pos in enumerate(transformed_positions):
                if distance(star2.iposition, pos) < match_offset:
                    result.append((stars1[j], star2))
                # cv2.line(img, stars1[j].iposition, (int(pos[0] + offset_width), pos[1]),  (random.randint(0, 255),
                #     random.randint(0, 255),
                #     random.randint(0, 255)), 2)
                
        cv2.circle(img, (int(p1[0]), int(p1[1])), 20, (255, 0,255), 5)
        cv2.circle(img, (offset_width + int(p3[0]), int(p3[1])), 20, (255, 0,255), 5)
        cv2.circle(img, (int(p2[0]), int(p2[1])), 20, (0, 255,255), 5)
        cv2.circle(img, (offset_width + int(p4[0]), int(p4[1])), 20, (0, 255,255), 5)

        for i, j in matches:
            print(f"{i} matches {j}")

        cv2.imwrite("temp2.jpg", img)
        return result

def distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def angle_between(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    det = v1[0]*v2[1] - v1[1]*v2[0]
    return math.atan2(det, dot)

def distance(a, b):
    return math.hypot(b[0] - a[0], b[1] - a[1])

def angle_between(v1, v2):
    dot = v1[0]*v2[0] + v1[1]*v2[1]
    det = v1[0]*v2[1] - v1[1]*v2[0]
    return math.atan2(det, dot)

def transform_between_lines(p1, p2, p3, p4):
    # Vector from p1 to p2 and p3 to p4
    v1 = (p2[0] - p1[0], p2[1] - p1[1])
    v2 = (p4[0] - p3[0], p4[1] - p3[1])

    # Scale
    len1 = distance(p1, p2)
    len2 = distance(p3, p4)
    scale = len2 / len1 if len1 != 0 else 0

    # Rotation
    angle = angle_between(v1, v2) 

    # Final translation: align transformed p1 with p3
    translation = p3  # we’ll apply rotation & scale around p1, then shift to p3

    return {
        'scale': scale,
        'rotation_radians': angle,
        'rotation_degrees': math.degrees(angle),
        'origin': p1,
        'translation': translation
    }

def apply_transform(transform, point):
    scale = transform['scale']
    angle = transform['rotation_radians']
    ox, oy = transform['origin']
    tx, ty = transform['translation']

    # Step 1: Translate point so origin becomes (0,0)
    px, py = point[0] - ox, point[1] - oy

    # Step 2: Scale
    px *= scale
    py *= scale

    # Step 3: Rotate
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    x_rot = cos_a * px - sin_a * py
    y_rot = sin_a * px + cos_a * py

    # Step 4: Translate to final position
    x_final = x_rot + tx
    y_final = y_rot + ty

    return (int(x_final), int(y_final))
