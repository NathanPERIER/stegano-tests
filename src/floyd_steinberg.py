
from PIL import Image

from typing import Tuple, Callable


def greyscale(rgb: Tuple[int,int,int]) -> int :
    return min(int(0.299 * rgb[0] + 0.587 * rgb[1] + 0.144 * rgb[2]), 255)

def threshold(grey: int) -> int :
    return 1 if grey > 127 else 0

def clamp(value: int) -> int :
    return 255 if value >= 255 else value if value >= 0 else 0

def floyd_steinberg(img: Image.Image, callback: Callable[[int,int,int],None]) :
    width, height = img.size
    pixels = img.load()
    correction      = [0.0] * width
    correction_next = [0.0] * width
    for i in range(height-1) :
        grey = clamp(greyscale(pixels[0,i]) + int(correction[0]))
        bw = threshold(grey)
        callback(0, i, bw)
        diff = grey - bw * 255
        correction[1]     += 8 * diff / 16
        correction_next[0] = 6 * diff / 16
        correction_next[1] = 2 * diff / 16
        for j in range(1, width-1) :
            grey = clamp(greyscale(pixels[j,i]) + int(correction[j]))
            bw = threshold(grey)
            callback(j, i, bw)
            diff = grey - bw * 255
            correction[j+1]      += 7 * diff / 16
            correction_next[j-1] += 3 * diff / 16
            correction_next[j]   += 5 * diff / 16
            correction_next[j+1]  = 1 * diff / 16
        grey = clamp(greyscale(pixels[width-1,i]) + int(correction[width-1]))
        bw = threshold(grey)
        callback(width-1, i, bw)
        diff = grey - bw * 255
        correction_next[width-2] += 6 * diff / 16
        correction_next[width-1] += 10 * diff / 16
        correction, correction_next = correction_next, correction
    for j in range(width-1) :
        grey = clamp(greyscale(pixels[j,height-1]) + int(correction[j]))
        bw = threshold(grey)
        callback(j,height-1, bw)
        diff = grey - bw * 255
        correction[j+1] = correction[j+1] + diff
    grey = clamp(greyscale(pixels[width-1,height-1]) + int(correction[width-1]))
    bw = threshold(grey)
    callback(width-1, height-1, bw)

