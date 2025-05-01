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

        # img = cv2.imread("connected.jpg")
        # height, width = img.shape[:2]
        
        # for i in range(0, len(possible_matches)):
        #     line1, line2 = possible_matches[i]

        #     print(f"found : {graph1.index(line1)} and {graph2.index(line2)} : ")
        #     print("offset : ", angleoffset)

        #     print("children 1 : ")
        #     for i, ang in line1.children:
        #         print("\t", i, ang)

        #     print("children 2 : ")
        #     for i, ang in line2.children:
        #         print("\t",i, ang)

        #     used_indexes1, used_indexes2 = [], []

        #     for i, child1 in enumerate(line1.children):
        #         child1line1, angle1 = child1
        #         for j, child2 in enumerate(line2.children):
        #             child1line2, angle2 = child2
        #             if abs(angle1 - angle2) < angleoffset and used_indexes1.count(i) == 0 and used_indexes2.count(j) == 0:
        #                 print("\tdiff = ", angle1 - angle2)
        #                 used_indexes1.append(i)
        #                 used_indexes2.append(j)

        #     temppos1 = line2.star1.iposition
        #     temppos2 = line2.star2.iposition

        #     cv2.line(img, line1.star1.iposition, (temppos1[0] + int(width / 2), temppos1[1]), (255, 255, 255))
        #     cv2.line(img, line1.star2.iposition, (temppos2[0] + int(width / 2), temppos2[1]), (255, 255, 255))
        #     cv2.imwrite("temp.jpg", img)




        
                
