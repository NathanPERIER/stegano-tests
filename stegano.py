#!/usr/bin/python3

import sys
from collections import deque
from PIL import Image
from tqdm import tqdm

from typing import Literal, Tuple, Callable

from src.floyd_steinberg import floyd_steinberg, threshold

def help() :
    print(f"{sys.argv[0]} [--wb] [--bg <bg_val>] <source_image> <stegano_image> <channel> <dest_image>")


def constrain_max_size(img: Image.Image, width: int, height: int) -> Image.Image :
    if img.width > width :
        h = (width * img.height) // img.width
        if h <= height : 
            return img.resize((width, h))
    if img.height > height :
        w = (height * img.width) // img.height
        return img.resize((w, height))
    return img


def apply_lsb_approx(value: int, lsb: int) :
    """
    Sets the bit as a mathematical approximation of the b/w image
    (i.e. 0 is black, 1 is white)
    """
    return value & 254 if lsb == 0 else value | 1

def apply_lsb_whiteboard(value: int, lsb: int) :
    """
    Sets the bit as if writing with a marker on a whitebaord
    (i.e. 0 is white, 1 is black)
    """
    return value | 1 if lsb == 0 else value & 254

def get_lsb_mapper(channel: Literal['r', 'g', 'b'], whiteboard: bool) -> Callable[[Tuple[int,int,int],int],Tuple[int,int,int]] :
    apply_lsb: Callable[[int,int],int] = apply_lsb_whiteboard if whiteboard else apply_lsb_approx
    pixel_lsb_mappers: dict[str,Callable[[Tuple[int,int,int],int],Tuple[int,int,int]]] = {
        'r': (lambda pixel, lsb: (apply_lsb(pixel[0], lsb), pixel[1], pixel[2])),
        'g': (lambda pixel, lsb: (pixel[0], apply_lsb(pixel[1], lsb), pixel[2])),
        'b': (lambda pixel, lsb: (pixel[0], pixel[1], apply_lsb(pixel[2], lsb)))
    }
    return pixel_lsb_mappers[channel]


class SteganoParams :

    def __init__(self) :
        self.channel: Literal['r', 'g', 'b'] = 'r'
        self.whiteboard: bool = False
        self.background: int = 0


class SteganoCallback :

    def __init__(self, img: Image.Image, width: int, height: int, params: SteganoParams, pbar: tqdm) :
        self.pixels = img.load()
        self.x_offset = (img.width  - width)  // 2
        self.y_offset = (img.height - height) // 2
        self.pixel_mapper = get_lsb_mapper(params.channel, params.whiteboard)
        self.pbar = pbar
        background_val = threshold(params.background)
        for x in range(0, self.x_offset) :
            for y in range(0, img.height) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], background_val)
                pbar.update(1)
        for x in range(width + self.x_offset, img.width) :
            for y in range(0, img.height) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], background_val)
                pbar.update(1)
        for y in range(0, self.y_offset) :
            for x in range(self.x_offset, width + self.x_offset) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], background_val)
                pbar.update(1)
        for y in range(height + self.y_offset, img.height) :
            for x in range(self.x_offset, width + self.x_offset) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], background_val)
                pbar.update(1)
    
    def __call__(self, x: int, y: int, v: int) :
        x += self.x_offset
        y += self.y_offset
        self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], v)
        self.pbar.update(1)


def main() :

    args = deque(sys.argv[1:])
    params = SteganoParams()

    if len(args) > 1 and args[0] in ['-h', '--help'] :
        help()
        sys.exit(0)

    if len(args) >= 1 and args[0] in ['--whiteboard', '--wb'] :
        params.whiteboard = True
        args.popleft()

    if len(args) >= 2 and args[0] in ['--background', '--bg'] :
        args.popleft()
        params.background = int(args.popleft())
    
    if len(args) < 4 :
        help()
        sys.exit(1)
    
    src_image_path = args[0]
    dst_image_path = args[3]
    stegano_image_path = args[1]

    stegano_channel = args[2].lower()
    if stegano_channel not in ['r', 'g', 'b'] :
        print(f"invalid channel: {stegano_channel} (should be one of 'r', 'g' or 'b')")
        sys.exit(1)
    params.channel = stegano_channel

    src_img = Image.open(src_image_path)
    stegano_img = constrain_max_size(Image.open(stegano_image_path), src_img.width, src_img.height)

    with tqdm(total = src_img.width*src_img.height, unit = 'px') as pbar :
        callback = SteganoCallback(src_img, stegano_img.width, stegano_img.height, params, pbar)
        floyd_steinberg(stegano_img, callback)
    src_img.save(dst_image_path)


if __name__ == '__main__' :
    main()
