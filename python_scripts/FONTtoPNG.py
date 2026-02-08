import sys
import os
import zlib


# This script converts "FONTALL.DAT" font file from IREM games like "PachiPara" and "Steambot Cronicles" to a rectangular PNG image.
PNG_SIGNATURE = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
IHDR = b'\x49\x48\x44\x52'
IDAT = b'\x49\x44\x41\x54'
IEND = b'\x49\x45\x4E\x44'
COLUMNS = 32
BUFFER_SIZE = 8192


def main():
    if len(sys.argv) == 1:
        print("Drop FONTALL.DAT.")
        input('Press Enter to close.')
        sys.exit()
    else:
        arg = sys.argv[1]
        try:
            infile = open(arg, 'rb')
        except:
            print(os.path.abspath(arg) + " failed to open.")
            input('Press Enter to close.')
            sys.exit()
    if infile.read(4) != b'FONT':
        infile.close()
        print(os.path.abspath(arg) + " not FONT.")
        input('Press Enter to close.')
        sys.exit()
    char_size = int.from_bytes(infile.read(4), byteorder='little', signed=False)
    byte_width = int.from_bytes(infile.read(4), byteorder='little', signed=False)
    height = int.from_bytes(infile.read(4), byteorder='little', signed=False)
    # This whole script is written with the assumption that bpp is always 2, so it might break otherwise.
    bpp = int.from_bytes(infile.read(4), byteorder='little', signed=False)
    width = byte_width * 8 // bpp
    # There is a value in these 12 bytes, but I don't understand what it relates to.
    infile.read(12)
    pixel_data = bytearray()
    while True:
        buffer = infile.read(char_size)
        if not buffer:
            break
        pixel_data += buffer
    infile.close()
    # Reorder bits to correct appearance.
    for i in range(len(pixel_data)):
        pixel_data[i] = ((pixel_data[i] & 192) >> 6) | ((pixel_data[i] & 48) >> 2) | ((pixel_data[i] & 12) << 2) | ((pixel_data[i] & 3) << 6)
    # Prepare PNG data.
    rows = -(-len(pixel_data) // (COLUMNS * char_size))
    png_data = bytearray()
    buffer = bytearray()
    png_data += PNG_SIGNATURE
    buffer += (width * COLUMNS).to_bytes(4, byteorder='big', signed=False)
    buffer += (height * rows).to_bytes(4, byteorder='big', signed=False)
    buffer += (bpp).to_bytes(1, byteorder='big', signed=False)
    buffer += b'\x00\x00\x00\x00'
    png_data += len(buffer).to_bytes(4, byteorder='big', signed=False)
    png_data += IHDR + buffer + zlib.crc32(IHDR + buffer).to_bytes(4, byteorder='big', signed=False)
    # Combine all chars into a single, nice looking, rectangle.
    new_pixel_data = bytearray()
    for i in range(rows):
        for j in range(height):
            for k in range(COLUMNS):
                x = (j * byte_width) + (k * char_size) + ((COLUMNS * char_size) * i)
                if x < len(pixel_data):
                    new_pixel_data += pixel_data[x:x + byte_width]
                else:
                    # Padding.
                    new_pixel_data += (0).to_bytes(byte_width)
    pixel_data = new_pixel_data
    del new_pixel_data
    filtered_pixel_data = bytearray()
    scanline = (bpp * width * COLUMNS) // 8
    for i in range(0, len(pixel_data), scanline):
        filtered_pixel_data += (0).to_bytes() + pixel_data[i:i + scanline]
    del pixel_data
    comp_buff = zlib.compress((filtered_pixel_data), level=6, wbits=15)
    del scanline
    del filtered_pixel_data
    pointer = 0
    loop = True
    while loop:
        if pointer + BUFFER_SIZE >= len(comp_buff):
            buffer = comp_buff[pointer:]
            loop = False
        else:
            buffer = comp_buff[pointer:pointer + BUFFER_SIZE]
        png_data += len(buffer).to_bytes(4, byteorder='big', signed=False)
        png_data += IDAT + buffer + zlib.crc32(IDAT + buffer).to_bytes(4, byteorder='big', signed=False)
        pointer += BUFFER_SIZE
    png_data += (0).to_bytes(4, byteorder='big', signed=False)
    png_data += IEND + zlib.crc32(IEND).to_bytes(4, byteorder='big', signed=False)
    with open(arg + ".png", 'wb') as outfile:
        outfile.write(png_data)
        print(os.path.abspath(arg + ".png") + " done.")
    input('Press Enter to close.')


if __name__ == '__main__':
    main()
