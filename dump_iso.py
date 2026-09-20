import sys
sys.path.insert(0, "python/")
import os
import hashlib
import subprocess
import csv
import png_helper
from tm2_to_png import tm2_to_png, swap_4bit_nibbles, fix_halved_transparanceis, unswizzle_palette
from fontall_to_png import font_to_png
from pachi_decoder import pachi_decode
from extract_strings import extract_from_file as get_strings
from graphics_whitelist import tm2_whitelist, pachi_whitelist
import terminal_keeper


# paths
dumps2iso = "tools/dumps2iso.exe"
dump_path = "dump/clean/"
dirty_path = "dump/dirty/"
xml_path = "dump/SLPS_25574.xml"


def verify_iso_md5(iso_path):
    with open(iso_path, 'rb') as infile:
        # add hashes for other versions of the game later?
        match hashlib.md5(infile.read()).hexdigest():
            # redump md5 hash of the 2.01 version iso.
            case "d4a0ea206a803b2bf6605747248d01f0":
                return iso_path
            case _:
                return False


def look_for_iso(dir_path):
    # verify all iso in the folder until correct is found
    dir_list = os.scandir(dir_path)
    for entry in dir_list:
        if entry.is_file() and entry.name.rsplit(".")[-1].upper() == "ISO":
            if iso_path := verify_iso_md5(entry):
                return iso_path
            else:
                continue
    return False


def dump_iso(iso_path):
    # dump iso using mkps2iso tool to "clean" folder
    subprocess.run([dumps2iso, "-o", dump_path, "-x", xml_path, iso_path])
    # update xml to rebuild from "dirty" folder
    import xml.etree.ElementTree as ET
    tree = ET.parse(xml_path)
    root = tree.getroot()
    root.attrib["image_name"] = "pachipara_12_patched.iso"
    root[1][0].attrib["source"] = "dirty/"
    tree.write(xml_path)
    return


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


def get_dat_fat_dict(file_list):
    # get dict with contents of all .DAT .FAT files
    dat_fat_dict = {}
    for file in file_list:
        if os.path.basename(file).rsplit(".")[-1].upper() in ["DAT", "FAT"]:
            with open(file, 'rb') as infile:
                data = get_fat_data(infile)
                if data:
                    if os.path.basename(file).rsplit(".")[-1].upper() == "FAT":
                        container = file.rsplit(".")[0] + ".DAT"
                    else:
                        container = file
                    if container not in dat_fat_dict:
                        dat_fat_dict[container] = data
                    else:
                        dat_fat_dict[container].update(data)
    return dat_fat_dict


# based on/copied from disaster_report.bms script for QuickBMS http://quickbms.aluigi.org
def get_fat_data(fat_file):
    if fat_file.read(4) != b'FAT ':
        return {}
    file_count = int.from_bytes(fat_file.read(4), 'little')
    fat_file.seek(0xFC)
    base_offset = int.from_bytes(fat_file.read(4), 'little')
    files = {}
    for i in range(file_count):
        file_offset = int.from_bytes(fat_file.read(4), 'little') + base_offset
        file_size = int.from_bytes(fat_file.read(4), 'little')
        fat_file.read(4)
        name_offset = int.from_bytes(fat_file.read(4), 'little')
        tmp = fat_file.tell()
        fat_file.seek(name_offset)
        name = bytearray()
        while (byte := fat_file.read(1)) != b'\x00':
            name += byte
        name = name.decode('ascii')
        files[name] = {"number" : i,
                       "file_offset" : file_offset,
                       "file_size" : file_size}
        fat_file.seek(tmp)
    return files


def save_dat_fat_dict(dat_fat_dict):
    # save .dat .fat data for reinsertion
    csv_path = "dump/dat_fat_list.csv"
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["container",
                         "file_order",
                         "file_name",
                         "file_offset",
                         "file_size"])
        for container in dat_fat_dict.keys():
            for file in dat_fat_dict[container].keys():
                file_offset = ("%X" % dat_fat_dict[container][file]["file_offset"]).zfill(8)
                file_size = ("%X" % dat_fat_dict[container][file]["file_size"]).zfill(8)
                writer.writerow([os.path.relpath(container, dump_path),
                                 dat_fat_dict[container][file]["number"],
                                 file,
                                 file_offset,
                                 file_size])
    print("{} created.".format(os.path.abspath(csv_path)))
    return


def extract_tm2_graphics(infile, file_name, offset, size):
    tm2_dir = "graphics/tm2/"
    sub_dir = os.path.basename(infile.name).rsplit(".")[0] + "/"
    if not os.path.isdir(tm2_dir + sub_dir):
        os.makedirs(tm2_dir + sub_dir, exist_ok=True)
    infile.seek(offset)
    png_data = tm2_to_png(bytearray(infile.read(size)))
    try:
        with open(tm2_dir + sub_dir + file_name + ".png", 'wb') as outfile:
            outfile.write(png_data)
            print("{} saved.".format(os.path.abspath(outfile.name)))
    except:
        print("Failed to save tm2: " + tm2_dir + sub_dir + file_name + ".png")


def extract_font(infile, file_name, offset, size):
    font_dir = "graphics/font/"
    if not os.path.isdir(font_dir):
        os.makedirs(font_dir, exist_ok=True)
    infile.seek(offset)
    png_data = font_to_png(bytearray(infile.read(size)))
    try:
        with open(font_dir + file_name + ".png", 'wb') as outfile:
            outfile.write(png_data)
            print("{} saved.".format(os.path.abspath(outfile.name)))
    except:
        print("Failed to save font: " + font_dir + file_name + ".png")


def extract_pachi_graphics(data : bytearray):
    header, pal_header, pal_data = get_ex_pachi_data()
    pal_entrys = {}
    for i in range(0, len(pal_header), 16):
        image_id = int.from_bytes(pal_header[i+8:i+12], 'little') - 1
        bpp = int.from_bytes(pal_header[i+6:i+8], 'little')
        palette_id = int.from_bytes(pal_header[i+12:i+16], 'little')
        match bpp:
            case 4:
                pal_offset = palette_id << 6
                pal_size = 0x40
            case 3:
                pal_offset = (palette_id * 0x400) + 0x2C40
                pal_size = 0x400
        pal_entrys[image_id] = (pal_offset, pal_size)
    for i in range(0, len(header), 16):
        img_id = i // 16
        file_name = str(img_id).zfill(4)
         # skip ripping graphics with no text
        if file_name not in pachi_whitelist:
            continue
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
        pixel_data = pachi_decode(data, offset, max_size)
        if bpp == 4:
            swap_4bit_nibbles(pixel_data)
            pixel_data = deinterlace_pixel_data(pixel_data, width)
        pal_start = pal_entrys[img_id][0]
        pal_size = pal_entrys[img_id][1]
        color_data = bytearray(pal_data[pal_start:pal_start+pal_size])
        fix_halved_transparanceis(color_data)
        if bpp == 8:
            color_data = unswizzle_palette(color_data)
        # save to png
        png_data = bytearray()
        png_data += png_helper.PNG_SIGNATURE
        png_helper.write_ihdr(png_data, width, height, bpp, 3)
        png_helper.write_plte(png_data, color_data)
        png_helper.write_trns(png_data, color_data)
        png_helper.write_idat(png_data, png_helper.compress_pixel_data(png_helper.filter_pixel_data(pixel_data, width, bpp), level=0))
        png_helper.write_iend(png_data)
        pachi_dir = "graphics/pachinko/"
        if not os.path.isdir(pachi_dir):
            os.makedirs(pachi_dir, exist_ok=True)
        try:
            with open(pachi_dir + file_name + ".png", 'wb') as outfile:
                outfile.write(png_data)
                print("{} saved.".format(os.path.abspath(outfile.name)))
        except:
            print("Failed to save pachi bitmap : " + pachi_dir + file_name + ".png")


def get_ex_pachi_data():
    # get header and palettes for EXCHR1.BIN from MAP/M_00_09.BIN file
    pachi_file_path = dump_path + "MAP/M_00_09.BIN"
    with open(pachi_file_path, 'rb') as infile:
        infile.seek(0x7BEAF0)
        header = infile.read(0x59E0)
        infile.seek(0x1248D0)
        pal_header = infile.read(0x5A10)
        infile.seek(0x12D2E0)
        pal_data = infile.read(0x36280)
    return header, pal_header, pal_data


def deinterlace_pixel_data(pixel_data : bytearray, width : int):
    # 4bpp bitmaps stored weirdly (for example 64x64 stored as 128x32 which then scaled by the game to normal proportions)
    # this code corrects proportions to make it easier to edit
    new_pixel_data = bytearray()
    for i in range(0, len(pixel_data), width):
        line = pixel_data[i:i+width]
        half_1 = bytearray()
        half_2 = bytearray()
        for j in range(0, width, 2):
            half_1 += ((line[j] & 0xF0) | ((line[j+1] & 0xF0) >> 4)).to_bytes(1, 'big')
            half_2 += (((line[j] & 0x0F) << 4) | (line[j+1] & 0x0F)).to_bytes(1, 'big')
        new_pixel_data += half_1 + half_2
    return new_pixel_data


def extract_sprite_data(file_list):
    # rip data that defines sprite sizes/positions
    texture_list = get_tm2_list()
    comparison_bytes = bytearray([0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                  0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80])
    data_dict = {}
    # go over binaries that can have sprite data
    for entry in file_list:
        if os.path.basename(entry).rsplit(".")[-1].upper() in ["BIN", "74"]:
            with open(entry, 'rb') as infile:
                data_dict[entry] = {}
                buffer = bytearray(0x20)
                # search for comparison bytes to find sprite entry
                while buffer:
                    tmp = infile.tell()
                    buffer = infile.read(0x20)
                    if buffer == comparison_bytes:
                        infile.seek(tmp - 0x30)
                        data_offset = infile.tell()
                        texture_name = str(int.from_bytes(infile.read(2), 'little')).zfill(5)
                        # skip ripping if not on the list
                        if texture_name not in texture_list:
                            infile.read(0x4E)
                            continue
                        width = int.from_bytes(infile.read(2), 'little')
                        height = int.from_bytes(infile.read(2), 'little')
                        infile.read(2)
                        x_start = int.from_bytes(infile.read(2), 'little')
                        y_start = int.from_bytes(infile.read(2), 'little')
                        x_end = int.from_bytes(infile.read(2), 'little')
                        y_end = int.from_bytes(infile.read(2), 'little')
                        x_screen_offset = int.from_bytes(infile.read(2), 'little')
                        y_screen_offset = int.from_bytes(infile.read(2), 'little')
                        data_dict[entry][data_offset] = {"texture_name" : texture_name,
                                                         "width" : width,
                                                         "height" : height,
                                                         "x_start" : x_start,
                                                         "y_start" : y_start,
                                                         "x_end" : x_end,
                                                         "y_end" : y_end,
                                                         "x_screen_offset" : x_screen_offset,
                                                         "y_screen_offset" : y_screen_offset}
                        infile.read(0x3C)
                    else:
                        infile.seek(tmp + 0x10)
    # save data to csv
    csv_path = "graphics/tm2/sprite_data.csv"
    with open(csv_path, 'w', encoding = 'utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["file",
                         "data_offset",
                         "texture_name",
                         "width",
                         "height",
                         "x_start",
                         "y_start",
                         "x_end",
                         "y_end",
                         "x_scrn_off",
                         "y_scrn_off",
                         "description"])
        for file in data_dict.keys():
            for offset in data_dict[file].keys():            
                writer.writerow([os.path.relpath(file, dump_path),
                                 ("%X" % offset).zfill(8),
                                 data_dict[file][offset]["texture_name"],
                                 data_dict[file][offset]["width"],
                                 data_dict[file][offset]["height"],
                                 data_dict[file][offset]["x_start"],
                                 data_dict[file][offset]["y_start"],
                                 data_dict[file][offset]["x_end"],
                                 data_dict[file][offset]["y_end"],
                                 data_dict[file][offset]["x_screen_offset"],
                                 data_dict[file][offset]["y_screen_offset"]])
    print("{} created.".format(os.path.abspath(csv_path)))


def get_tm2_list():
    # get list of ripped tm2s so you only get data for those
    tm2_dir = "graphics/tm2/"
    tm2_list = get_file_list(tm2_dir)
    texture_list = []
    for entry in tm2_list:
        tm2_id = os.path.basename(entry).rsplit(".")[0]
        if tm2_id not in texture_list:
            texture_list.append(tm2_id)
    return texture_list


def extract_strings(file_list):
    if not os.path.isdir("text/"):
            os.makedirs("text/", exist_ok=True)
    for entry in file_list:
        if os.path.basename(entry).rsplit(".")[-1].upper() in ["BIN", "74"]:
            strings = get_strings(entry)
            if not strings:
                continue
            csv_path = "text/" + os.path.basename(entry) + ".csv"
            with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(["block",
                                 "j_offset",
                                 "j_string",
                                 "e_string",
                                 "pointer"])
                for i in range(len(strings)):
                    for string in strings[i]:
                        j_offset = ("%X" % string[0]).zfill(8)
                        pointer = ("%X" % string[2]).zfill(8)
                        writer.writerow([i,
                                         ("%X" % string[0]).zfill(8),
                                         string[1],
                                         "",
                                         ("%X" % string[2]).zfill(8) if string[2] != 0 else ""])
            print("{} created.".format(os.path.abspath(csv_path)))
    cleanup_m_00_09()


def cleanup_m_00_09():
    # clean up garbage data
    csv_path = "text/M_00_09.BIN.csv"
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, delimiter = ';', quotechar = '"')
        clean_data = []
        for row in reader:
            if row["block"] == "0" and int(row["j_offset"], 16) < 0x7A0000:
                continue
            else:
                clean_data.append([row["block"],
                                   row["j_offset"],
                                   row["j_string"],
                                   row["e_string"],
                                   row["pointer"]])
    with open(csv_path, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["block",
                         "j_offset",
                         "j_string",
                         "e_string",
                         "pointer"])
        for line in clean_data:
            writer.writerow(line)
    print("{} cleansed.".format(os.path.abspath(csv_path)))


def main():
    message = "Type the number of the command and confirm with ENTER key.\n" \
              "1: Dump both ISO and game assets.\n" \
              "2: Dump only ISO.\n"
    print(message)
    while True:
        command = input("Command: ").strip()
        if command in ["1", "2"]:
            break
    # if no path argument search for iso
    if len(sys.argv) == 1:
        work_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        iso_path = look_for_iso(work_dir)
    # if single argument provided assume it's iso for verification
    elif len(sys.argv) == 2 and sys.argv[1].rsplit(".")[-1].upper() == "ISO":
        iso_path = verify_iso_md5(sys.argv[1])
    else:
        print("Usage: Put ISO in work folder or drop it on this script.")
        sys.exit()
    if iso_path:
        dump_iso(iso_path)
        file_list = get_file_list(dump_path)
        dat_fat_dict = get_dat_fat_dict(file_list)
        save_dat_fat_dict(dat_fat_dict)
        # copy clean data to dirty directory
        def copy_clean_data():
            print("\nMaking a copy of clean dump.")
            for entry in file_list:
                directory = os.path.dirname(os.path.relpath(entry, dump_path))
                directory = dirty_path + directory + "/" if directory else dirty_path 
                file = os.path.basename(entry)
                if not os.path.isdir(directory):
                    os.makedirs(directory)
                with open(entry, 'rb') as clean, open(directory + file, 'wb') as dirty:
                    dirty.write(clean.read())
        copy_clean_data()
        print("\n")
    else:
        print("FAIL: correct ISO was not provided.")
        sys.exit()
    if command == "1":
        # dump all relevant assets from extracted files
        print("Dumping assets...") 
        # extracting data from .DAT files (TM2s, FONT, pachinko bitmaps)
        for entry in dat_fat_dict.keys():
            print("Extracting contents from " + entry)
            container_file = open(entry, 'rb')
            for item in dat_fat_dict[entry].keys():
                file_name = os.path.basename(item)
                offset = dat_fat_dict[entry][item]["file_offset"]
                size = dat_fat_dict[entry][item]["file_size"]
                # TM2s
                if file_name.rsplit(".")[-1].upper() == "TM2":
                    if file_name.rsplit(".")[0] in tm2_whitelist:
                        extract_tm2_graphics(container_file, file_name, offset, size)
                    else:
                        continue
                # FONTALL.DAT
                elif file_name == "FONTALL.DAT":
                   extract_font(container_file, file_name, offset, size)
                # pachinko bitmaps EXCHR1.BIN
                elif file_name == "EXCHR1.BIN":
                    container_file.seek(offset)
                    extract_pachi_graphics(container_file.read(size))
            container_file.close()
        extract_sprite_data(file_list)
        extract_strings(file_list)
    print("FINISHED!")


if __name__ == '__main__':
    main()
