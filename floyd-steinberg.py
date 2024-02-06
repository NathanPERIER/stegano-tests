#!/usr/bin/python3

import sys
from collections import deque
from PIL import Image

from src.floyd_steinberg import floyd_steinberg

def help() :
    print(f"{sys.argv[0]} <source_image> <dest_image>")


class FloydSteinbergCallback :

    def __init__(self, width: int, height: int, whiteboard: bool) :
        self.img = Image.new(mode="RGB", size=(width, height))
        self.pixels = self.img.load()
        self.mapper = (lambda v: 255 - v*255) if whiteboard else (lambda v: v*255)
    
    def __call__(self, x: int, y: int, v: int) :
        g = self.mapper(v)
        self.pixels[x,y] = (g, g, g)
    
    def get_image(self) -> Image.Image :
        return self.img


def main() :

    args = deque(sys.argv[1:])

    if len(args) > 1 and args[0] in ['-h', '--help'] :
        help()
        sys.exit(0)
    
    whiteboard = False
    if len(args) >= 1 and args[0] in ['--whiteboard', '--wb'] :
        whiteboard = True
        args.popleft()
    
    if len(args) < 2 :
        help()
        sys.exit(1)
    
    src_image_path = args[0]
    dst_image_path = args[1]

    img = Image.open(src_image_path)
    callback = FloydSteinbergCallback(img.width, img.height, whiteboard)
    floyd_steinberg(img, callback)
    callback.get_image().save(dst_image_path)


if __name__ == '__main__' :
    main()
