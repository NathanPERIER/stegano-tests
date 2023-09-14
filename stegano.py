#!/usr/bin/python3

import sys
from PIL import Image
from tqdm import tqdm

from typing import Literal, Tuple, Callable

from src.floyd_steinberg import floyd_steinberg

def help() :
    print(f"{sys.argv[0]} <source_image> <stegano_image> <channel> <dest_image>")


def constrain_max_size(img: Image.Image, width: int, height: int) -> Image.Image :
    if img.width > width :
        h = (width * img.height) // img.width
        if h <= height : 
            return img.resize((width, h))
    if img.height > height :
        w = (height * img.width) // img.height
        return img.resize((w, height))
    return img


def apply_lsb(value: int, lsb: int) :
    return value & 254 if lsb == 0 else value | 1

pixel_lsb_mappers: dict[str,Callable[[Tuple[int,int,int],int],Tuple[int,int,int]]] = {
    'r': (lambda pixel, lsb: (apply_lsb(pixel[0], lsb), pixel[1], pixel[2])),
    'g': (lambda pixel, lsb: (pixel[0], apply_lsb(pixel[1], lsb), pixel[2])),
    'b': (lambda pixel, lsb: (pixel[0], pixel[1], apply_lsb(pixel[2], lsb)))
}


class SteganoCallback :

    def __init__(self, img: Image.Image, width: int, height: int, channel: Literal['r', 'g', 'b'], pbar: tqdm) :
        self.pixels = img.load()
        self.x_offset = (img.width  - width)  // 2
        self.y_offset = (img.height - height) // 2
        self.pixel_mapper = pixel_lsb_mappers[channel]
        self.pbar = pbar
        for x in range(0, self.x_offset) :
            for y in range(0, img.height) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], 0)
                pbar.update(1)
        for x in range(width + self.x_offset, img.width) :
            for y in range(0, img.height) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], 0)
                pbar.update(1)
        for y in range(0, self.y_offset) :
            for x in range(self.x_offset, width + self.x_offset) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], 0)
                pbar.update(1)
        for y in range(height + self.y_offset, img.height) :
            for x in range(self.x_offset, width + self.x_offset) :
                self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], 0)
                pbar.update(1)
    
    def __call__(self, x: int, y: int, v: int) :
        x += self.x_offset
        y += self.y_offset
        self.pixels[x,y] = self.pixel_mapper(self.pixels[x,y], v)
        self.pbar.update(1)


def main() :

    if len(sys.argv) > 1 and sys.argv[0] in ['-h', '--help'] :
        help()
        sys.exit(0)
    
    if len(sys.argv) < 5 :
        help()
        sys.exit(1)
    
    src_image_path = sys.argv[1]
    dst_image_path = sys.argv[4]
    stegano_image_path = sys.argv[2]

    stegano_channel = sys.argv[3].lower()
    if stegano_channel not in ['r', 'g', 'b'] :
        print(f"invalid channel: {stegano_channel} (should be one of 'r', 'g' or 'b')")
        sys.exit(1)

    src_img = Image.open(src_image_path)
    stegano_img = constrain_max_size(Image.open(stegano_image_path), src_img.width, src_img.height)

    with tqdm(total = src_img.width*src_img.height) as pbar :
        callback = SteganoCallback(src_img, stegano_img.width, stegano_img.height, stegano_channel, pbar)
        floyd_steinberg(stegano_img, callback)
    src_img.save(dst_image_path)


if __name__ == '__main__' :
    main()
