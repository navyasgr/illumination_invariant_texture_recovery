import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

def load_image(path, grayscale=True):
    if grayscale:
        img = Image.open(path).convert('L')
    else:
        img = Image.open(path).convert('RGB')
    return np.array(img)

def save_image(img_array, path):
    img = Image.fromarray(np.uint8(img_array * 255))
    img.save(path)

def show_images(images, titles, figsize=(15,8)):
    n = len(images)
    plt.figure(figsize=figsize)
    for i in range(n):
        plt.subplot(1, n, i+1)
        if images[i].ndim == 2:
            plt.imshow(images[i], cmap='gray')
        else:
            plt.imshow(images[i])
        plt.title(titles[i])
        plt.axis('off')
    plt.tight_layout()
    plt.show()
