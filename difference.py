class Difference:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.found = False

    def contains(self, click_x, click_y, tolerance=5):
        """
        Check if the click is within the difference area, with tolerance padding.
        """
        return (
            self.x - tolerance <= click_x <= self.x + self.w + tolerance
            and
            self.y - tolerance <= click_y <= self.y + self.h + tolerance
        )