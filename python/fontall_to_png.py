import sys
import os
import png_helper


# this script converts "FONTALL.DAT" font file from IREM games like "PachiPara" and "Steambot Cronicles"
# to a single png image where all the characters neatly placed on a grid instead of having 1000+ 24x24 images.

# how many columns the grid will have
COLUMNS = 32


def swap_2bit_nibbles(pixel_data : bytearray):
    for i in range(len(pixel_data)):
        pixel_data[i] = ((pixel_data[i] & 0xC0) >> 6) | ((pixel_data[i] & 0x30) >> 2) | ((pixel_data[i] & 0x0C) << 2) | ((pixel_data[i] & 0x03) << 6)


def stacked_bitmaps_to_grid(pixel_data : bytearray, bitmap_size : int, height : int, columns : int = 32):
    # amount of rows for the grid = (total size of pixel data / size of individual image / num of columns) rounded up
    rows = -(-len(pixel_data) // bitmap_size // columns)
    new_pixel_data = bytearray()
    # width of individual image in bytes = size of individual image / its height
    byte_width = bitmap_size // height
    # idea behind these nested loops is to add lines of each individual image to fill columns of the final output
    for i in range(rows):
        for j in range(height):
            for k in range(columns):
                # x = offset to line
                x = (j * byte_width) + (k * bitmap_size) + ((columns * bitmap_size) * i)
                if x < len(pixel_data):
                    new_pixel_data += pixel_data[x:x + byte_width]
                else:
                    # Padding.
                    new_pixel_data += (0).to_bytes(byte_width, 'big')
    return new_pixel_data


def font_to_png(raw_data : bytearray):
    if raw_data[:4] != bytearray(b'FONT'):
        return "Not FONT data."
    char_size = int.from_bytes(raw_data[4:8], 'little')
    height = int.from_bytes(raw_data[12:16], 'little')
    bpp = int.from_bytes(raw_data[16:20], 'little')
    width = (char_size // height) * (8 // bpp)
    pixel_data = bytearray(raw_data[32:])
    swap_2bit_nibbles(pixel_data)
    pixel_data = stacked_bitmaps_to_grid(pixel_data, char_size, height, COLUMNS)
    rows = -(-len(pixel_data) // char_size // COLUMNS)
    png_data = bytearray()
    png_data += png_helper.PNG_SIGNATURE
    png_helper.write_ihdr(png_data, width * COLUMNS, height * rows, bpp, 0)
    png_helper.write_idat(png_data, png_helper.compress_pixel_data(png_helper.filter_pixel_data(pixel_data, width * COLUMNS, bpp), level=0))
    png_helper.write_iend(png_data)
    return png_data
    

def main():
    if len(sys.argv) == 1:
        print("Drop FONTALL.DAT on the py file.")
        input('Press Enter to close.')
        sys.exit()
    else:
        arg = sys.argv[1]
        try:
            raw_data = open(arg, 'rb').read()
        except:
            print(os.path.abspath(arg) + " failed to open.")
            input('Press Enter to close.')
            sys.exit()
        png_data = font_to_png(raw_data)
        if type(png_data) is str:
            print(os.path.abspath(arg) + " ERROR: " + png_data)
        else:
            with open(arg + ".png", 'wb') as outfile:
                outfile.write(png_data)
                print(os.path.abspath(arg + ".png") + " done.")
    input('Press Enter to close.')


if __name__ == '__main__':
    main()
