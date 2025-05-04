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

        self.lines = []

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
