import sys
import os
import png_helper

# TM2 specifications https://openkh.dev/common/tm2.html
# basic tm2 to png converter that only supports image color types 3, 4, 5

def tm2_to_png(tm2_data : bytearray, half_trans : bool = True):
    if tm2_data[:4] != bytearray(b'TIM2'):
        return "not TM2 data"
    color_size = int.from_bytes(tm2_data[20:24], 'little')
    pixel_size = int.from_bytes(tm2_data[24:28], 'little')
    match int.from_bytes(tm2_data[35:36], 'little'):
        case 3:
            bpp = 32
            color_type = 6
        case 4:
            bpp = 4
            color_type = 3
        case 5:
            bpp = 8
            color_type = 3
        case _:
            return "bpp not supported"
    width = int.from_bytes(tm2_data[36:38], 'little')
    height = int.from_bytes(tm2_data[38:40], 'little')
    pixel_data = bytearray(tm2_data[64:64 + pixel_size])
    if color_type == 3:
        color_data = bytearray(tm2_data[64 + pixel_size:])
        if half_trans:
            fix_halved_transparanceis(color_data)
    elif color_type == 6 and half_trans:
        fix_halved_transparanceis(pixel_data)
    if bpp == 8 and color_type == 3:
        color_data = unswizzle_palette(color_data)
    if bpp == 4:
        swap_4bit_nibbles(pixel_data)
    png_data = bytearray()
    png_data += png_helper.PNG_SIGNATURE
    png_helper.write_ihdr(png_data, width, height, bpp if bpp != 32 else 8, color_type)
    if 'color_data' in locals():
        png_helper.write_plte(png_data, color_data)
        png_helper.write_trns(png_data, color_data)
    #png_helper.write_text(png_data, "TM2_HEADER", tm2_data[:64].hex())
    png_helper.write_idat(png_data, png_helper.compress_pixel_data(png_helper.filter_pixel_data(pixel_data, width, bpp), level=0))
    png_helper.write_iend(png_data)
    return png_data


def fix_halved_transparanceis(data : bytearray):
    for i in range(0, len(data), 4):
        if data[i + 3] > 0 and data[i + 3] <= 128:
            data[i + 3] = (data[i + 3] << 1) - 1
    return


def unswizzle_palette(color_data : bytearray):
    if padding := bytearray(0x400 - len(color_data)):
        print("busted palette")
        color_data += padding
    sorted_palette = bytearray()
    for i in range(0, 1024, 128):
        chunk_1 = color_data[i:i + 32]
        chunk_2 = color_data[i + 32:i + 64]
        chunk_3 = color_data[i + 64:i + 96]
        chunk_4 = color_data[i + 96:i + 128]
        sorted_palette += chunk_1 + chunk_3 + chunk_2 + chunk_4
    return sorted_palette


def swap_4bit_nibbles(pixel_data : bytearray):
    for i in range(len(pixel_data)):
        pixel_data[i] = ((pixel_data[i] << 4) | (pixel_data[i] >> 4)) & 0xFF


def main():
    if len(sys.argv) == 1:
        print("Drop TIM2 on the py file.")
        input('Press Enter to close.')
        sys.exit()
    else:
        for arg in sys.argv[1:]:
            try:
                raw_data = open(arg, 'rb').read()
            except:
                print(os.path.abspath(arg) + " failed to open.")
                continue
            png_data = tm2_to_png(raw_data)
            if type(png_data) is str:
                print(os.path.abspath(arg) + " ERROR: " + png_data)
                continue
            else:
                with open(arg + ".png", 'wb') as outfile:
                    outfile.write(png_data)
                    print(os.path.abspath(arg + ".png") + " done.")
    input('Press Enter to close.')


if __name__ == '__main__':
    main()
