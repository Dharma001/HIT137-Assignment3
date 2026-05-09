from abc import ABC, abstractmethod
import cv2
import numpy as np


class Effect(ABC):
    """
    Base class for all effects.
    """
    @abstractmethod
    def apply(self, region):
        """
        Apply the effect to the given region.
        """
        pass


class BlurEffect(Effect):
    """
    Applies Gaussian blur to the region.
    """
    def apply(self, region):
        return cv2.GaussianBlur(region, (15, 15), 0)


class BrightnessEffect(Effect):
    """
    Increases brightness of the region.
    """
    def apply(self, region):
        return cv2.convertScaleAbs(region, alpha=1.2, beta=30)


class ColorEffect(Effect):
    """
    Changes the color by maximizing the green channel.
    """
    def apply(self, region):
        modified = region.copy()
        modified[:, :, 1] = 255
        return modified


class PixelEffect(Effect):
    """
    Pixelates the region.
    """
    def apply(self, region):
        h, w = region.shape[:2]
        temp = cv2.resize(region, (w // 10, h // 10), interpolation=cv2.INTER_LINEAR)
        return cv2.resize(temp, (w, h), interpolation=cv2.INTER_NEAREST)


class NoiseEffect(Effect):
    """
    Adds random noise to the region.
    """
    def apply(self, region):
        noise = np.random.normal(0, 25, region.shape).astype(np.uint8)
        return cv2.add(region, noise)