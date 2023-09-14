#!/usr/bin/python3

import sys
from PIL import Image

from src.floyd_steinberg import floyd_steinberg

def help() :
    print(f"{sys.argv[0]} <source_image> <dest_image>")


class FloydSteinbergCallback :

    def __init__(self, width: int, height: int) :
        self.img = Image.new(mode="RGB", size=(width, height))
        self.pixels = self.img.load()
    
    def __call__(self, x: int, y: int, v: int) :
        self.pixels[x,y] = (v*255, v*255, v*255)
    
    def get_image(self) -> Image.Image :
        return self.img


def main() :

    if len(sys.argv) > 1 and sys.argv[0] in ['-h', '--help'] :
        help()
        sys.exit(0)
    
    if len(sys.argv) < 3 :
        help()
        sys.exit(1)
    
    src_image_path = sys.argv[1]
    dst_image_path = sys.argv[2]

    img = Image.open(src_image_path)
    callback = FloydSteinbergCallback(img.width, img.height)
    floyd_steinberg(img, callback)
    callback.get_image().save(dst_image_path)


if __name__ == '__main__' :
    main()
