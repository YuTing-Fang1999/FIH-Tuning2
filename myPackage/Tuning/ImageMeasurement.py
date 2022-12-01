import cv2
import numpy as np
import math
from scipy.signal import convolve2d

def get_sharpness(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return np.sqrt(cv2.Laplacian(img, cv2.CV_64F).var())

def get_chroma_stdev(img):
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    y, u, v = cv2.split(img_yuv)
    return u.std()+v.std()

# Reference: J. Immerkær, “Fast Noise Variance Estimation”, Computer Vision and Image Understanding, Vol. 64, No. 2, pp. 300-302, Sep. 1996 [PDF]
def get_luma_stdev(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    H, W = img.shape

    M = [[1, -2, 1],
            [-2, 4, -2],
            [1, -2, 1]]

    sigma = np.sum(np.sum(np.absolute(convolve2d(img, M))))
    sigma = sigma * math.sqrt(0.5 * math.pi) / (6 * (W-2) * (H-2))

    return sigma

def get_average_gnorm(img):
        # https://stackoverflow.com/questions/6646371/detect-which-image-is-sharper
        I = img.copy()
        I = cv2.cvtColor(I, cv2.COLOR_BGR2GRAY).astype('float64')
        gy, gx = np.gradient(I)
        gnorm = np.sqrt(gx**2 + gy**2)
        sharpness = np.average(gnorm)
        return np.round(sharpness, 4)