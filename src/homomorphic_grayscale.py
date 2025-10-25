"""
homomorphic_grayscale.py
------------------------
Author       : Navyashree N
Description  : Homomorphic Filtering for Illumination-Invariant Texture Recovery
               This script processes a single grayscale image of a textured surface
               and separates the illumination (low frequency) and reflectance (high frequency)
               components using frequency-domain techniques. Manual and FFT implementations are included.
"""

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

class HomomorphicTextureRecovery:
    """
    Homomorphic filtering for grayscale images.
    Separates illumination (L) and reflectance (R) from an observed image I = R * L.
    Supports manual DFT (educational) and FFT (practical) methods.
    """

    def __init__(self, cutoff_frequency=30, filter_order=2):
        """
        Initialize filter parameters
        :param cutoff_frequency: D0, cutoff for Butterworth filter
        :param filter_order: n, order of Butterworth filter (sharpness)
        """
        self.D0 = cutoff_frequency
        self.n = filter_order

    # ================= Manual DFT (Educational) =================
    def compute_2d_dft_manual(self, image):
        """
        Compute 2D Discrete Fourier Transform manually
        Complexity: O(M^2 N^2), use only for small images
        """
        M, N = image.shape
        F = np.zeros((M, N), dtype=complex)
        for u in range(M):
            for v in range(N):
                sum_val = 0.0 + 0.0j
                for x in range(M):
                    for y in range(N):
                        angle = -2 * np.pi * (u * x / M + v * y / N)
                        sum_val += image[x, y] * np.exp(1j * angle)
                F[u, v] = sum_val
        return F

    def compute_2d_idft_manual(self, F):
        """
        Compute 2D Inverse Discrete Fourier Transform manually
        """
        M, N = F.shape
        image = np.zeros((M, N), dtype=complex)
        for x in range(M):
            for y in range(N):
                sum_val = 0.0 + 0.0j
                for u in range(M):
                    for v in range(N):
                        angle = 2 * np.pi * (u * x / M + v * y / N)
                        sum_val += F[u, v] * np.exp(1j * angle)
                image[x, y] = sum_val
        return image / (M * N)

    # ================= FFT (Practical) =================
    def compute_2d_fft(self, image):
        """Compute 2D FFT using numpy (fast)"""
        return np.fft.fft2(image)

    def compute_2d_ifft(self, F):
        """Compute inverse FFT"""
        return np.fft.ifft2(F)

    # ================= Filter Creation =================
    def create_butterworth_highpass(self, shape):
        """Create Butterworth high-pass filter"""
        rows, cols = shape
        center_row, center_col = rows // 2, cols // 2
        H = np.zeros((rows, cols), dtype=float)
        for u in range(rows):
            for v in range(cols):
                D = np.sqrt((u - center_row) ** 2 + (v - center_col) ** 2)
                if D == 0:
                    D = 1e-10  # Avoid division by zero
                H[u, v] = 1 / (1 + (self.D0 / D) ** (2 * self.n))
        return H

    def create_butterworth_lowpass(self, shape):
        """Create Butterworth low-pass filter"""
        rows, cols = shape
        center_row, center_col = rows // 2, cols // 2
        H = np.zeros((rows, cols), dtype=float)
        for u in range(rows):
            for v in range(cols):
                D = np.sqrt((u - center_row) ** 2 + (v - center_col) ** 2)
                H[u, v] = 1 / (1 + (D / self.D0) ** (2 * self.n))
        return H

    # ================= Main Processing =================
    def process_grayscale_image(self, image_path, use_manual_dft=False):
        """
        Complete pipeline:
        1. Logarithmic transform
        2. Fourier transform
        3. Apply high-pass and low-pass filters
        4. Inverse transform
        5. Exponential recovery
        """
        img = Image.open(image_path).convert('L')
        I = np.array(img, dtype=float) / 255.0  # Normalize

        epsilon = 1e-6
        log_I = np.log(I + epsilon)  # Step 1: Log transform

        # Step 2: Fourier Transform
        if use_manual_dft and I.shape[0] <= 64 and I.shape[1] <= 64:
            F = self.compute_2d_dft_manual(log_I)
        else:
            F = self.compute_2d_fft(log_I)
        F_shifted = np.fft.fftshift(F)

        # Step 3: Apply filters
        H_high = self.create_butterworth_highpass(log_I.shape)
        H_low = self.create_butterworth_lowpass(log_I.shape)

        F_high = F_shifted * H_high  # Reflectance
        F_low = F_shifted * H_low    # Illumination

        # Step 4: Inverse transform
        F_high = np.fft.ifftshift(F_high)
        F_low = np.fft.ifftshift(F_low)

        if use_manual_dft and I.shape[0] <= 64 and I.shape[1] <= 64:
            log_R = np.real(self.compute_2d_idft_manual(F_high))
            log_L = np.real(self.compute_2d_idft_manual(F_low))
        else:
            log_R = np.real(self.compute_2d_ifft(F_high))
            log_L = np.real(self.compute_2d_ifft(F_low))

        # Step 5: Exponential recovery
        R = np.exp(log_R)
        L = np.exp(log_L)

        # Normalize for visualization
        R = (R - R.min()) / (R.max() - R.min() + epsilon)
        L = (L - L.min()) / (L.max() - L.min() + epsilon)

        return R, L

    # ================= Visualization =================
    def visualize_results(self, image_path, R, L):
        """Visualize original, log domain, frequency spectrum, illumination, reflectance, and verification"""
        img = Image.open(image_path).convert('L')
        I = np.array(img) / 255.0

        fig = plt.figure(figsize=(18, 12))

        # Original
        plt.subplot(2, 3, 1)
        plt.imshow(I, cmap='gray')
        plt.title('Original Image I(x,y)')
        plt.axis('off')

        # Log domain
        plt.subplot(2, 3, 2)
        plt.imshow(np.log(I + 1e-6), cmap='gray')
        plt.title('Log Domain')
        plt.axis('off')

        # Frequency spectrum
        plt.subplot(2, 3, 3)
        F = np.fft.fftshift(np.fft.fft2(np.log(I + 1e-6)))
        plt.imshow(np.log(np.abs(F) + 1), cmap='hot')
        plt.title('Frequency Spectrum')
        plt.axis('off')

        # Illumination
        plt.subplot(2, 3, 4)
        plt.imshow(L, cmap='gray')
        plt.title('Estimated Illumination L̂(x,y)')
        plt.axis('off')

        # Reflectance
        plt.subplot(2, 3, 5)
        plt.imshow(R, cmap='gray')
        plt.title('Recovered Texture R̂(x,y)')
        plt.axis('off')

        # Verification
        plt.subplot(2, 3, 6)
        plt.imshow(R * L, cmap='gray')
        plt.title('Verification: R̂ × L̂')
        plt.axis('off')

        plt.tight_layout()
        plt.savefig('images/output/reflectance_vs_illumination.png', dpi=300)
        plt.show()

# ================= Demonstration =================
if __name__ == "__main__":
    processor = HomomorphicTextureRecovery(cutoff_frequency=30, filter_order=2)
    image_path = 'images/texture_input.jpeg'  
    R, L = processor.process_grayscale_image(image_path)
    processor.visualize_results(image_path, R, L)
    print("✅ Grayscale texture recovery complete!")
