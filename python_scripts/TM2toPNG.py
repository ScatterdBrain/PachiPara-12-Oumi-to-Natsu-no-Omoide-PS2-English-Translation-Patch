import sys
import os
import zlib


# TM2 specifications https://openkh.dev/common/tm2.html
# PNG specifications https://www.w3.org/TR/PNG-Introduction.html
PNG_SIGNATURE = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
IHDR = b'\x49\x48\x44\x52'
PLTE = b'\x50\x4C\x54\x45'
TRNS = b'\x74\x52\x4E\x53'
IDAT = b'\x49\x44\x41\x54'
IEND = b'\x49\x45\x4E\x44'
BUFFER_SIZE = 16384


def main():
    if len(sys.argv) == 1:
        print("Drop TIM2.")
        input('Press Enter to close.')
        sys.exit()
    else:
        for arg in sys.argv[1:]:
            try:
                infile = open(arg, 'rb')
            except:
                print(os.path.abspath(arg) + " failed to open.")
                continue
            if infile.read(4) != b'TIM2':
                print(os.path.abspath(arg) + " not TIM2.")
                infile.close()
                continue
            infile.seek(20)
            color_size = int.from_bytes(infile.read(4), byteorder='little', signed=False)
            pixel_size = int.from_bytes(infile.read(4), byteorder='little', signed=False)
            infile.seek(35)
            match int.from_bytes(infile.read(1), byteorder='little', signed=False):
                case 3:
                    bpp = 32
                case 4:
                    bpp = 4
                case 5:
                    bpp = 8
                case _:
                    print(arg + " not supported.")
                    infile.close()
                    continue
            width = int.from_bytes(infile.read(2), byteorder='little', signed=False)
            height = int.from_bytes(infile.read(2), byteorder='little', signed=False)
            infile.seek(64)
            pixel_data = bytearray(infile.read(pixel_size))
            # Fix transparencies.
            if color_size != 0:
                color_data = bytearray(infile.read(color_size))
                for i in range(0, len(color_data), 4):
                    if color_data[i + 3] > 0 and color_data[i + 3] <= 128:
                        color_data[i + 3] = (color_data[i + 3] << 1) - 1
            elif color_size == 0 and bpp == 32:
                for i in range(0, len(pixel_data), 4):
                    if pixel_data[i + 3] > 0 and pixel_data[i + 3] <= 128:
                        pixel_data[i + 3] = (pixel_data[i + 3] << 1) - 1
            if bpp == 8:
                # Unswizzle palette.
                sorted_palette = bytearray()
                for i in range(0, 1024, 128):
                    chunk_1 = color_data[i:i + 32]
                    chunk_2 = color_data[i + 32:i + 64]
                    chunk_3 = color_data[i + 64:i + 96]
                    chunk_4 = color_data[i + 96:i + 128]
                    sorted_palette += chunk_1 + chunk_3 + chunk_2 + chunk_4
                color_data = sorted_palette
                del sorted_palette
            if bpp == 4:
                # Swap 4bit nibles.
                for i in range(len(pixel_data)):
                    pixel_data[i] = ((pixel_data[i] << 4) & 255) | ((pixel_data[i] >> 4) % 255)
            infile.close()
            # Convert to PNG data.
            del color_size
            del pixel_size
            png_data = bytearray()
            buffer = bytearray()
            png_data += PNG_SIGNATURE
            buffer += (width).to_bytes(4, byteorder='big', signed=False)
            buffer += (height).to_bytes(4, byteorder='big', signed=False)
            match bpp:
                case 4 | 8:
                    buffer += (bpp).to_bytes(1, byteorder='big', signed=False)
                    buffer += b'\x03\x00\x00\x00'
                case 32:
                    buffer += (8).to_bytes(1, byteorder='big', signed=False)
                    buffer += b'\x06\x00\x00\x00'
            png_data += len(buffer).to_bytes(4, byteorder='big', signed=False)
            png_data += IHDR + buffer + zlib.crc32(IHDR + buffer).to_bytes(4, byteorder='big', signed=False)
            if 'color_data' in locals():
                plte_chunk = bytearray()
                trns_chunk = bytearray()
                for i in range(0, len(color_data), 4):
                    plte_chunk += color_data[i:i + 3]
                    trns_chunk += color_data[i + 3].to_bytes(1)
                buffer = plte_chunk
                del plte_chunk
                png_data += len(buffer).to_bytes(4, byteorder='big', signed=False)
                png_data += PLTE + buffer + zlib.crc32(PLTE + buffer).to_bytes(4, byteorder='big', signed=False)
                buffer = trns_chunk
                del trns_chunk
                png_data += len(buffer).to_bytes(4, byteorder='big', signed=False)
                png_data += TRNS + buffer + zlib.crc32(TRNS + buffer).to_bytes(4, byteorder='big', signed=False)
            filtered_pixel_data = bytearray()
            scanline = bpp * width // 8
            for i in range(0, len(pixel_data), scanline):
                filtered_pixel_data += (0).to_bytes() + pixel_data[i: i + scanline]
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

