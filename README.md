
# Stegano tests

This is a small test to embed an image in the lest significant bytes of another image. For this, we take the greyscale of the image we want embedded and we apply the Floyd-Steinberg algorithm to get a representation using only two colours (black and white). We then use the least significant bits from one bit plane of the other image to store these values.

## Usage

To get a preview of the Floyd-Steinberg algorithm :

```bash
./floyd-steinberg.py [--wb] <source_image> <dest_image>
```

To embed the image in another :

```bash
./stegano.py [--wb] [--bg <bg_val>] <source_image> <stegano_image> <channel> <dest_image>
```

The destination image can be tested with tools such as [CyberChef](https://gchq.github.io/CyberChef/#recipe=View_Bit_Plane('Red',0)).

> Note : for this to work, the destination image must be in a lossless format such as `png` (NOT `jpg`)

### Whiteboard mode

The `--wb` argument enables the "whiteboard" mode.

By default, one would expect black (`#000000`) to be encoded as `0` and white (`#FFFFFF`) to be encoded as `1`. However, some decoders actually seem to do the opposite, kind of like if the embedded image was a whiteboard or a paper sheet where `0` represents an empty cell and `1` represents a cell that has been drawn on. 

### Background value

If the size of the image to be embedded does not match the main image's, it will be fitted in the centre (potentially with downscaling if it is too big). The `--bg` option is used to specify the 8-bit value (0-255) which should be used for filling the empty spaces. It will ultimately be converted to `0` or `1` but it is kept as an 8-bit integer to enable potential changes in the future.

The default value is `0`, if you don't like the filling colour you can just set it to `255` and you will get the opposite colour.
