import cv2
import math

class Star:
    def __init__(self, x : float, y : float, b : float, r : float):
        """Create a star object to keep track of star properties

        Args:
            x (float): X position on image
            y (float): Y position on image
            b (float): Average brightness
            r (float): Star radius
        """
        self.x = x
        self.y = y
        self.b = b
        self.r = r

    @property
    def position(self):
        return (self.x, self.y)

    @property
    def iposition(self):
        return (int(self.x), int(self.y))

    def __eq__(self, value):
        if type(value) is not Star: return False
        return self.x == value.x and \
            self.y == value.y and \
            self.b == value.b and \
            self.r == value.r
    
    def __ne__(self, value):
        return not self == value

    def __str__(self):
        return f"({self.x}, {self.y}, {self.b}, {self.r})"


class LineNode:
    def __init__(self, star1 : Star, star2 : Star):
        """Create a new LineNode object to connect two stars

        Args:
            star1 (Star): First star object
            star2 (Star): Second star object
        """
        self.star1 = star1
        self.star2 = star2
        self.length = math.hypot(star1.x - star2.x, star1.y - star2.y)
        self.children : list[tuple[LineNode, float]] = []

    def add_child(self, line : "LineNode"):
        """Connect another LineNode to the current line

        Args:
            line (LineNode): The line to connect, must have one common point.

        Returns:
            bool: True if child was added, false otherwise
        """

        if self == line: return False
        if not LineNode.has_one_common_star(self, line): return False
        if self.children.count(line) != 0: return False

        angle, _ = LineNode.calc_inner_angle(self, line)

        self.children.append((line, angle))
        return True

    @staticmethod
    def get_connetion_order(line1 : "LineNode", line2 : "LineNode"):
        """Returns the order of points in which the lines are connected (assumes they are connected)."""

        if not LineNode.has_one_common_star(line1, line2): raise Exception("Lines must have 1 commnon star.")

        common = LineNode.get_common_star(line1, line2)
        p1 = line1.star2.iposition if common == line1.star1 else line1.star1.iposition
        p2 = line2.star2.iposition if common == line2.star1 else line2.star1.iposition
        return (p1, common.iposition, p2)

    @staticmethod
    def get_inner_angle_order(line1 : "LineNode", line2 : "LineNode"):
        """Returns the order of points in which the lines are connected (assumes they are connected)."""

        if not LineNode.has_one_common_star(line1, line2): raise Exception("Lines must have 1 commnon star.")
        
        angle, start, end = LineNode.calc_angle(line1, line2)

        if angle <= 180:
            return LineNode.get_connetion_order(line1, line2)
        else:
            return LineNode.get_connetion_order(line2, line1)

    @staticmethod
    def has_one_common_star(line1 : "LineNode", line2 : "LineNode"):
        """Check if two lines have exactly one common star."""
        return (line1.star1 == line2.star1 and line1.star2 != line2.star2) or \
            (line1.star1 != line2.star1 and line1.star2 == line2.star2) or \
            (line1.star1 == line2.star2 and line1.star2 != line2.star1) or \
            (line1.star1 != line2.star2 and line1.star2 == line2.star1)

    @staticmethod 
    def get_common_star(line1 : "LineNode", line2 : "LineNode") -> Star | None:
        """Returns the common star between lines.

        Returns:
            (Star | None): Star - when there's exactly 1 common star, None otherwise.
        """

        if not LineNode.has_one_common_star(line1, line2): return None
        if line1.star1 == line2.star1: return line1.star1
        if line1.star2 == line2.star2: return line1.star2
        if line1.star1 == line2.star2: return line1.star1
        if line1.star2 == line2.star1: return line1.star2

    @staticmethod
    def calc_angle(line1 : "LineNode", line2 : "LineNode"):
        """Calculate the angle between two lines in degrees, assumes they are connected.

        Returns:
            int: angle between the lines.
        """

        p0, p1, p2 = LineNode.get_connetion_order(line1, line2)

        # Vectors from p1 to p0 and p1 to p2
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])

        angle1 = math.degrees(math.atan2(v1[1], v1[0]))
        angle2 = math.degrees(math.atan2(v2[1], v2[0]))

        start_angle = angle1
        end_angle = angle2

        if start_angle > end_angle: end_angle += 360

        result = end_angle - start_angle

        return (result, start_angle, end_angle)

    @staticmethod
    def calc_inner_angle(line1 : "LineNode", line2 : "LineNode"):
        p0, p1, p2 = LineNode.get_inner_angle_order(line1, line2)

        # Vectors from p1 to p0 and p1 to p2
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])

        angle1 = math.degrees(math.atan2(v1[1], v1[0]))
        angle2 = math.degrees(math.atan2(v2[1], v2[0]))

        start_angle = angle1
        end_angle = angle2

        result = min((end_angle - start_angle) % 360, (start_angle - end_angle) % 360)

        return (result, start_angle)

    def __eq__(self, value):
        if type(value) is not LineNode: return False
        return (self.star1 == value.star1 and self.star2 == value.star2) or \
            (self.star1 == value.star2 and self.star2 == value.star1)
            
    def __ne__(self, value):
        return not self == value
    
    def __str__(self):
        return f"({self.star1}, {self.star2}, children={len(self.children)})"


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
    def match_stars(graph1 : list[LineNode], graph2 : list[LineNode], min_matches=5, offset=0.01):
        possible_matches : list[tuple[LineNode, LineNode]] = []

        angleoffset = 360 * offset

        def childrenSort(graph : list["LineNode"]): 
            graph.sort(key=lambda line: len(line.children), reverse=True)

        childrenSort(graph1)
        childrenSort(graph2)

        def test_lines(line1 : LineNode, line2 : LineNode):
            temp_matches = []
            failed_matches = []
            used_indexes1 = []
            used_indexes2 = []

            print(f"comparing : {graph1.index(line1)} and {graph2.index(line2)} : ")

            for i, child1 in enumerate(line1.children):
                childline1, angle1 = child1
                for j, child2 in enumerate(line2.children):
                    childline2, angle2 = child2
                    if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
                        print("\tdiff = ", angle1 - angle2)
                        temp_matches.append((childline1.children, childline2.children, i, j))
                        used_indexes1.append(i)
                        used_indexes2.append(j)

            if len(temp_matches) >= min_matches:
                print(f"found : {graph1.index(line1)} and {graph2.index(line2)} !!! ")
                possible_matches.append((line1, line2))
                return True
            return False

        def find_match():
            # Assume image was scaled proportionally - Compare angles only
            for line1 in graph1:
                if len(line1.children) < 2: continue
                for line2 in graph2:
                    if len(line2.children) < 2: continue
                    result = test_lines(line1, line2)
                    if result: return

        find_match()

        img = cv2.imread("connected.jpg")
        height, width = img.shape[:2]
        
        for i in range(0, len(possible_matches)):
            line1, line2 = possible_matches[i]

            print(f"found : {graph1.index(line1)} and {graph2.index(line2)} : ")
            print("offset : ", angleoffset)

            print("children 1 : ")
            for i, ang in line1.children:
                print("\t", i, ang)

            print("children 2 : ")
            for i, ang in line2.children:
                print("\t",i, ang)

            used_indexes1, used_indexes2 = [], []

            for i, child1 in enumerate(line1.children):
                child1line1, angle1 = child1
                for j, child2 in enumerate(line2.children):
                    child1line2, angle2 = child2
                    if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
                        print("\tdiff = ", angle1 - angle2)
                        used_indexes1.append(i)
                        used_indexes2.append(j)

            temppos1 = line2.star1.iposition
            temppos2 = line2.star2.iposition

            cv2.line(img, line1.star1.iposition, (temppos1[0] + int(width / 2), temppos1[1]), (255, 255, 255))
            cv2.line(img, line1.star2.iposition, (temppos2[0] + int(width / 2), temppos2[1]), (255, 255, 255))
            cv2.imwrite("temp.jpg", img)




        
                
