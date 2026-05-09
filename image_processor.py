import cv2
import random
from difference import Difference
from effects import BlurEffect, BrightnessEffect, ColorEffect, PixelEffect, NoiseEffect


class ImageProcessor:
    """
    Handles image processing and difference creation.
    """

    def __init__(self):
        self.differences = []
        self.effects = [
            BlurEffect(),
            BrightnessEffect(),
            ColorEffect(),
            PixelEffect(),
            NoiseEffect()
        ]

    def create_differences(self, image, difficulty='medium'):
        """
        Creates 5 non-overlapping differences on the image based on difficulty.
        """
        modified = image.copy()
        height, width, _ = image.shape
        self.differences = []

        # Difficulty affects difference size
        if difficulty == 'easy':
            min_size, max_size = 60, 100
        elif difficulty == 'medium':
            min_size, max_size = 40, 80
        else:  # hard
            min_size, max_size = 20, 60

        while len(self.differences) < 5:
            diff_width = random.randint(min_size, max_size)
            diff_height = random.randint(min_size, max_size)

            x = random.randint(0, width - diff_width - 1)
            y = random.randint(0, height - diff_height - 1)

            overlap = False
            # Prevent overlapping differences
            for diff in self.differences:
                if (
                    x < diff.x + diff.w
                    and x + diff_width > diff.x
                    and y < diff.y + diff.h
                    and y + diff_height > diff.y
                ):
                    overlap = True
                    break

            if overlap:
                continue

            region = modified[y:y + diff_height, x:x + diff_width]
            effect = random.choice(self.effects)
            modified[y:y + diff_height, x:x + diff_width] = effect.apply(region)

            self.differences.append(
                Difference(x, y, diff_width, diff_height)
            )

        return modified