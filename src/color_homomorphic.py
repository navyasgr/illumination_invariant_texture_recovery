import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

class ColorHomomorphicFiltering:
    """
    Multi-channel illumination correction preserving color ratios
    """
    def __init__(self, cutoff=30, order=2, gamma_low=0.3, gamma_high=2.0):
        self.D0 = cutoff
        self.n = order
        self.gamma_low = gamma_low
        self.gamma_high = gamma_high

    # Homomorphic filter creation
    def create_homomorphic_filter(self, shape):
        rows, cols = shape
        center_row, center_col = rows // 2, cols // 2
        H = np.zeros((rows, cols))
        for u in range(rows):
            for v in range(cols):
                D = np.sqrt((u - center_row)**2 + (v - center_col)**2)
                if D == 0:
                    D = 1e-10
                H_hp = 1.0 / (1.0 + (self.D0 / D)**(2 * self.n))
                H[u, v] = (self.gamma_high - self.gamma_low) * H_hp + self.gamma_low
        return H

    # Normalize image to [0,1]
    def normalize_image(self, img):
        img = np.clip(img, 0, None)
        img = img / (np.percentile(img, 99) + 1e-6)
        return np.clip(img, 0, 1)

    # Method 1: Independent channel processing
    def method1_independent_channels(self, rgb_image):
        H, W, C = rgb_image.shape
        result = np.zeros_like(rgb_image, dtype=float)
        for channel in range(3):
            I_channel = rgb_image[:, :, channel] / 255.0
            log_I = np.log(I_channel + 1e-6)
            F = np.fft.fft2(log_I)
            F_shifted = np.fft.fftshift(F)
            H_filter = self.create_homomorphic_filter((H, W))
            F_filtered = F_shifted * H_filter
            F_filtered = np.fft.ifftshift(F_filtered)
            log_result = np.real(np.fft.ifft2(F_filtered))
            result[:, :, channel] = np.exp(log_result)
        return self.normalize_image(result)

    # Method 2: Chromaticity preserved
    def method2_chromaticity_preserved(self, rgb_image):
        rgb = rgb_image / 255.0
        epsilon = 1e-6
        intensity = (rgb[:, :, 0] + rgb[:, :, 1] + rgb[:, :, 2]) / 3.0
        sum_channels = np.sum(rgb, axis=2) + epsilon
        r_chrom = rgb[:, :, 0] / sum_channels
        g_chrom = rgb[:, :, 1] / sum_channels
        b_chrom = rgb[:, :, 2] / sum_channels
        log_I = np.log(intensity + epsilon)
        F = np.fft.fft2(log_I)
        F_shifted = np.fft.fftshift(F)
        H_filter = self.create_homomorphic_filter(intensity.shape)
        F_filtered = F_shifted * H_filter
        F_filtered = np.fft.ifftshift(F_filtered)
        intensity_corrected = np.exp(np.real(np.fft.ifft2(F_filtered)))
        result = np.zeros_like(rgb)
        result[:, :, 0] = r_chrom * intensity_corrected * 3
        result[:, :, 1] = g_chrom * intensity_corrected * 3
        result[:, :, 2] = b_chrom * intensity_corrected * 3
        return self.normalize_image(result)
