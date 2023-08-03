#!/usr/bin/python3

from PIL import Image

from src.floyd_steinberg import floyd_steinberg


def main() :
    img = Image.open('pie.jpg')
    floyd_steinberg(img)


if __name__ == '__main__' :
    main()
