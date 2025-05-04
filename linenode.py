from star import Star
import math 

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
        self.children1 : list[LineNode] = []
        self.children2 : list[LineNode] = []

    def add_child(self, line : "LineNode", angle : float):
        self.children.append((line, angle))

        if LineNode.get_common_star(self, line) == self.star1: self.children1.append(line)
        else: self.children2.append(line)

    @property
    def lengths(self):
        return (abs(self.star1.position[0] - self.star2.position[0]), abs(self.star1.position[1] - self.star2.position[1]))

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
        if line1.star1 == line2.star1: return line1.star1
        if line1.star2 == line2.star2: return line1.star2
        if line1.star1 == line2.star2: return line1.star1
        if line1.star2 == line2.star1: return line1.star2
        return None

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

