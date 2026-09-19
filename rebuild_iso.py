import sys
sys.path.insert(0, "python/")
import os
import csv
from PIL import Image
import imagequant
from tm2_to_png import swap_4bit_nibbles, fix_halved_transparanceis, unswizzle_palette
from pachi_decoder import pachi_encode, pachi_decode
from reinsert_strings import get_strings, reinsert_strings
import subprocess
import time
import terminal_keeper


# paths
mkps2iso = "tools/mkps2iso.exe"
dump_path = "dump/clean/"
dirty_path = "dump/dirty/"
xml_path = "dump/SLPS_25574.xml"
armips = "tools/armips.exe"
xdelta = "tools/xdelta3-3.1.0-x86_64.exe"


def get_dat_fat_dict():
    dat_fat_path = "dump/dat_fat_list.csv"
    dat_fat_dict = {}
    with open(dat_fat_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ';', quotechar = '"')
        for row in reader:
            data = {row["file_name"] : (int(row["file_offset"], 16), int(row["file_size"], 16))}
            if row["container"] not in dat_fat_dict:
                dat_fat_dict[row["container"]] = data
            else:
                dat_fat_dict[row["container"]].update(data)
    return dat_fat_dict


def reinsert_tm2(dat_file, png_image, offset, size):
    # use original tim2 header
    dat_file.seek(offset)
    dat_file.read(0x14)
    palette_size = int.from_bytes(dat_file.read(4), 'little')
    bitmap_size = int.from_bytes(dat_file.read(4), 'little')
    dat_file.read(0x7)
    match int.from_bytes(dat_file.read(1), 'big'):
        case 3:
            bpp = 32
            mode = 'RGBA'
            max_colors = 16777216
            pixel_data = bytearray(png_image.convert(mode = mode, palette = Image.Palette.ADAPTIVE, colors = max_colors).tobytes())
            halve_transparancy(pixel_data)
            color_data = None
        case 4:
            bpp = 4
            mode = 'P'
            max_colors = 16
            png_image = imagequant.quantize_pil_image(png_image, dithering_level = 1.0, max_colors = max_colors, min_quality = 0, max_quality = 100)
            png_image = png_image.convert(mode = mode, palette = Image.Palette.ADAPTIVE, colors = max_colors)
            color_data = bytearray(png_image.convert('PA').getpalette('RGBA'))[:0x40]
            remove_imagequant_green(color_data)
            halve_transparancy(color_data)
            pixel_data = bytearray(png_image.tobytes())
            pixel_data = bpp8_to_bpp4(pixel_data)
            swap_4bit_nibbles(pixel_data)
        case 5:
            bpp = 8
            mode = 'P'
            max_colors = 256
            png_image = imagequant.quantize_pil_image(png_image, dithering_level = 1.0, max_colors = max_colors, min_quality = 0, max_quality = 100)
            png_image = png_image.convert(mode = mode, palette = Image.Palette.ADAPTIVE, colors = max_colors)
            color_data = bytearray(png_image.convert('PA').getpalette('RGBA'))
            remove_imagequant_green(color_data)
            halve_transparancy(color_data)
            color_data = unswizzle_palette(color_data)
            pixel_data = bytearray(png_image.tobytes())
        case _:
            return
    # write pixel data if it's the same size
    if len(pixel_data) == bitmap_size:
        dat_file.seek(offset + 0x40)
        dat_file.write(pixel_data)
    else:
        print("{} pixel size mismatch".format(png_image.filename))
        return
    # write color data if it's the same size
    if color_data:
        if len(color_data) == palette_size:
            dat_file.seek(offset + bitmap_size + 0x40)
            dat_file.write(color_data)
        else:
            print("{} color size mismatch".format(png_image.filename))
            return
    # update resolution in case it was changed
    size = png_image.size
    dat_file.seek(offset + 0x24)
    dat_file.write(size[0].to_bytes(2, 'little'))
    dat_file.write(size[1].to_bytes(2, 'little'))
    return


def halve_transparancy(data : bytearray):
    for i in range(0, len(data), 4):
        if data[i + 3] > 0:
            data[i + 3] = (data[i + 3] >> 1) + 1


def remove_imagequant_green(data : bytearray):
    # imagequant quantazes fully transparent color as b'GpL\x00'... cute
    # in some games it leads to black backgrounds being green or green bleeding on pixels with transparency
    for i in range(0, len(data), 4):
        if data[i + 3] == 0:
            data[i],data[i+1],data[i+2] = 0,0,0


def bpp8_to_bpp4(pixel_data : bytearray):
    new_pixel_data = bytearray()
    for i in range(0, len(pixel_data), 2):
        new_pixel_data += (((pixel_data[i] << 4) | pixel_data[i+1]) & 0xFF).to_bytes(1, 'big')
    return new_pixel_data


def reinsert_font(dat_file, png_image, offset, size):
    # expecting edit that uses 4 color greyscale palette from dark to bright
    # if edit is non-paletted then PIL will convert it, but the palette order is upredictable
    png_image = png_image.convert(mode = 'P', palette = Image.Palette.ADAPTIVE, colors = 4)
    width = 24
    height = 24
    columns = 32
    rows = -(-png_image.height // height)
    # convert bitmap for each char on a grid to bytes
    raw_data = bytearray()
    for i in range(rows):
        y = height * i
        for j in range(columns):
            x = width * j
            buffer = png_image.crop((x, y, x + width, y + height)).tobytes()
            # turn 4 bytes 8bpp to 1 byte 2bpp
            for k in range(0, len(buffer), 4):
                raw_data += (buffer[k + 3] << 6 | buffer[k + 2] << 4 | buffer[k + 1] << 2 | buffer[k]).to_bytes(1, 'big')
    dat_file.seek(offset + 0x20)
    dat_file.write(raw_data[:size])
    return


def reinsert_pachi_graphics(dat_file, ex_offset, ex_size):
##    ex_size = 0x96E3F0 # potential max size for compressed blob
    dat_file.seek(ex_offset)
    original_data = bytearray(dat_file.read(ex_size))
    # get exchr1 header
    with open(dirty_path + "MAP/M_00_09.BIN", 'rb') as infile:
        infile.seek(0x7BEAF0)
        header = infile.read(0x59E0)
    # get dict of pachi graphics
    pachi_graphics = {}
    for i in range(0, len(header), 16):
        image_id = i // 16
        width = int.from_bytes(header[i:i+4], 'little')
        height = int.from_bytes(header[i+4:i+8], 'little')
        bpp = int.from_bytes(header[i+8:i+12], 'little')
        offset = int.from_bytes(header[i+12:i+16], 'little')
        match bpp:
            case 0:
                bpp = 4
            case 1:
                bpp = 8
            case _:
                pass
        max_size = int((width * height) // (8 // bpp))
        comp_size = int.from_bytes(header[i+28:i+32], 'little') - offset
        if i == len(header) - 16:
            comp_size = len(original_data) - offset
        pachi_graphics[image_id] = {
            "width" : width,
            "height" : height,
            "bpp" : bpp,
            "offset" : offset,
            "max_size" : max_size,
            "comp_size": comp_size
            }
    # if graphic edit exist compress and write it to buffer else write original
    new_data = bytearray()
    # keep track of bitmap offsets
    new_header_offsets = []
    for graphic in pachi_graphics.keys():
        new_header_offsets.append(len(new_data))
        start = pachi_graphics[graphic]["offset"]
        end = start + pachi_graphics[graphic]["comp_size"]
        path = "graphics/pachinko/" + str(graphic).zfill(4) + ".png"
        if os.path.isfile(path):
            png_image = Image.open(path, 'r')
            # if non paletted or wrong bitmap size or same bitmap write original
            match pachi_graphics[graphic]["bpp"]:
                case 4:
                    pixel_data = bytearray(png_image.tobytes())
                    pixel_data = bpp8_to_bpp4(pixel_data)
                    pixel_data = interlace_pixel_data(pixel_data, pachi_graphics[graphic]["width"])
                    swap_4bit_nibbles(pixel_data)
                case 8:
                    pixel_data = bytearray(png_image.tobytes())
                case _:
                    pixel_data = bytearray()
            compare_data = pachi_decode(original_data[start:end], 0, pachi_graphics[graphic]["max_size"])
            if len(pixel_data) == pachi_graphics[graphic]["max_size"] and pixel_data != compare_data:
                print("Writing {} to EXCHR1.BIN".format(path))
                pixel_data = pachi_encode(pixel_data)
                new_data += pixel_data + bytearray(int(16 - (len(pixel_data) % 16)))
                continue
        new_data += original_data[start:end]
    # if new exchr1 data same or smaller size write it otherwise skip
    if len(new_data) <= ex_size:
        dat_file.seek(ex_offset)
        dat_file.write(new_data)
        print("EXCHR1.BIN replaced succesfully")
    else:
        print("EXCHR1.BIN is too big")
        return
    # update header for compressed data
    with open(dirty_path + "MAP/M_00_09.BIN", 'r+b') as infile:
        infile.seek(0x7BEAF0)
        for item in new_header_offsets:
            infile.read(12)
            infile.write(item.to_bytes(4, 'little'))
    return


def interlace_pixel_data(pixel_data : bytearray, width : int):
    new_pixel_data = bytearray()
    for i in range(0, len(pixel_data), width):
        line = bytearray()
        half_1 = pixel_data[i:i+width//2]
        half_2 = pixel_data[i+width//2:i+width]
        for j in range(0, width//2):
            line += ((half_1[j] & 0xF0) | ((half_2[j] & 0xF0) >> 4)).to_bytes(1, 'big')
            line += (((half_1[j] & 0x0F) << 4) | (half_2[j] & 0x0F)).to_bytes(1, 'big')
        new_pixel_data += line
    return new_pixel_data


def write_strings():
    targets = [
        ("text/M_00_09.BIN.csv", "MAP/M_00_09.BIN"),
        ("text/M_01_01.BIN.csv", "MAP/M_01_01.BIN"),
        ("text/M_02_01.BIN.csv", "MAP/M_02_01.BIN"),
        ("text/M_02_02.BIN.csv", "MAP/M_02_02.BIN"),
        ("text/M_03_01.BIN.csv", "MAP/M_03_01.BIN"),
        ("text/M_04_01.BIN.csv", "MAP/M_04_01.BIN"),
        ("text/M_CMN.BIN.csv", "MAP/M_CMN.BIN"),
        ("text/SLPS_255.74.csv", "SLPS_255.74")
        ]
    for target in targets:
        print("Writing strings to {}.".format(dirty_path + target[1])) 
        reinsert_strings(dirty_path + target[1], get_strings(target[0]))
    return


def apply_hacks():
    def get_file_list(directory):
        # recursively get list of all files from directory and its subdirectories
        file_list = []
        dir_list = os.scandir(directory)
        for entry in dir_list:
            if entry.is_file():
                file_list.append(entry.path)
            elif entry.is_dir():
                file_list += get_file_list(entry.path)
        return file_list
    file_list = get_file_list("hacks/")
    print("Applying hacks.")
    for entry in file_list:
        if entry.rsplit(".")[-1].lower() == "asm":
            subprocess.run([armips, entry])
    

def main():
    # reinsert graphics into .dat files
    dat_fat_dict = get_dat_fat_dict()
    for container in dat_fat_dict.keys():
        container_file = open(dirty_path + container, 'r+b')
        for file in dat_fat_dict[container].keys():
            match file.rsplit('.')[-1]:
                case "TM2":
                    path = "graphics/tm2/" + os.path.basename(container).rsplit('.')[0] + "/" + os.path.basename(file) + ".png"
                    if os.path.isfile(path):
                        png_image = Image.open(path, 'r')
                        offset = dat_fat_dict[container][file][0]
                        size = dat_fat_dict[container][file][1]
                        reinsert_tm2(container_file, png_image, offset, size)
                        print("Written {} to {}".format(png_image.filename, container))
                        png_image.close()
                    else:
                        pass
                case "DAT":
                    if os.path.basename(file) == "FONTALL.DAT":
                        path = "graphics/font/" + os.path.basename(file) + ".png"
                        if os.path.isfile(path):
                            png_image = Image.open(path, 'r')
                            offset = dat_fat_dict[container][file][0]
                            size = dat_fat_dict[container][file][1]
                            reinsert_font(container_file, png_image, offset, size)
                            print("Written {} to {}".format(png_image.filename, container))
                            png_image.close()
                        else:
                            pass
                case "BIN":
                    if os.path.basename(file) == "EXCHR1.BIN":
                        offset = dat_fat_dict[container][file][0]
                        size = dat_fat_dict[container][file][1]
                        reinsert_pachi_graphics(container_file, offset, size)
        container_file.close()
    write_strings()
    apply_hacks()
    # rebuild iso
    print("\n")
    subprocess.run([mkps2iso, "-y", xml_path])


if __name__ == '__main__':
    main()
