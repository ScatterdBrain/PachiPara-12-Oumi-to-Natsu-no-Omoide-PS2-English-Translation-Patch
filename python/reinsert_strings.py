import sys
import os
import csv


targets = {
    "SLPS_255.74" : {
        "ptr_offset" : 0xFFD00,
        "blocks" : [
            (0x171340, 0xF78),
            (0x1726D0, 0x15C0),
            (0x180E20, 0xD30),
            (0x18C080, 0x3078),
            (0x193E40, 0xB78),
            (0x19DD70, 0x228),
            (0x19EAF8, 0xF40),
            (0x19FF70, 0x20),
            (0x1A0410, 0x750),
            (0x1A42F0, 0x50),
            (0x1A4680, 0xC0),
            (0x1A7DE8, 0x150),
            (0x1AE2E0, 0x218),
            (0x1AFA00, 0x6B8),
            (0x1B6370, 0x590),
            (0x1B69E0, 0x918),
            (0x1B85C0, 0xB0),
            (0x1B8B38, 0x2C0),
            (0x1B9050, 0x978),
            (0x1B9CA8, 0x11F8),
            (0x1BBA78, 0xA8),
            (0x1BBC28, 0x28D0),
            (0x1C17A0, 0x48),
            (0x1C1848, 0x658),
            (0x1C27F0, 0x3488)#,
            #(0x1D8129, 0x92D)
            ]
        },
    "M_00_09.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x7C7650, 0x1A95),
            (0x7C9120, 0x209),
            (0x7C9620, 0xB36),
            (0x7CA4D0, 0xC00),
            (0x7CB260, 0x360),
            (0x7CB7A0, 0x3C3),
            (0x7CBC20, 0x3BC),
            (0x7CC146, 0xFA),
            (0x7CC280, 0x6E),
            (0x7CC360, 0x80),
            (0x7CC610, 0x1260)
            ]
        },
    "M_01_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x47C90, 0x48),
            (0x47CF0, 0xD130),
            (0x5A860, 0x11370)
            ]
        },
    "M_02_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x4F0B0, 0x13700),
            (0x66CF0, 0xF318)
            ]
        },
    "M_02_02.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x4B58, 0xBC0)
            ]
        },
    "M_03_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x24120, 0x178),
            (0x24320, 0x94E0),
            (0x2FB80, 0x3E68)
            ]
        },
    "M_04_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "blocks" : [
            (0x3340, 0xC50)
            ]
        },
    "M_CMN.BIN" : {
        "ptr_offset" : 0x38D580,
        "blocks" : [
            (0x84380, 0x6050),
            (0x8C1A8, 0x5B30),
            (0x93768, 0x5E00),
            (0x9B1C8, 0x5CC8),
            (0xA2828, 0xD20),
            (0xA3958, 0x4E38),
            (0xA9F80, 0xA0),
            (0xAA050, 0x3368),
            (0xAE320, 0x4C8),
            (0xAE9F0, 0x38C0),
            (0xC3E50, 0x1078),
            (0xC88B0, 0x5468),
            (0xCF7B0, 0xC8),
            (0xCFB00, 0x88),
            (0xCFDA0, 0x58),
            (0xD00A0, 0x500),
            (0xD0958, 0x2B0),
            (0xD0DE0, 0x30),
            (0xD0F30, 0x2630),
            (0xD4CE8, 0x188)
            ]
        }
    }


def get_strings(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter = ';', quotechar = '"')
            string_list = []
            for row in reader:
                if (e_string := row["e_string"]) != "":
                    string_list.append((e_string, row["pointer"]))
                else:
                    string_list.append((row["j_string"], row["pointer"]))
    return string_list


def reinsert_strings(bin_path, string_list):
    file = os.path.basename(bin_path)
    pointer_offset = targets[file]["ptr_offset"]
    blocks = []
    for block in targets[file]["blocks"]:
        blocks.append([block[0], block[1]])
    with open(bin_path, 'r+b') as binfile:
        # clear the blocks before writing
        for block in blocks:
            binfile.seek(block[0])
            binfile.write(bytearray(block[1]))
        # keep track of strings with pointers to avoid writing repeated strings and instead just update pointers
        ptr_strings = {}
        # encode the string
        for string in string_list:
            try:
                bin_string = string[0].encode('shiftjisx0213')
            except:
                # in case encoder fails
                print("{} failed to encode: {}".format(file, string[0]))
                bin_string = ("{}_{}".format(file, string_list.index(string))).encode('shiftjisx0213')
            bin_string += b'\x00'
            if string[1] != "":
                pointer = int(string[1], 16)
                # if string not a repeat search for a block that fits string length and write it otherwise only write pointer 
                if bin_string not in ptr_strings.keys():
                    for block in blocks:
                        if (string_length := len(bin_string)) <= block[1]:
                            string_offset = block[0]
                            string_pointer = string_offset + pointer_offset
                            binfile.seek(string_offset)
                            binfile.write(bin_string)
                            binfile.seek(pointer)
                            binfile.write(string_pointer.to_bytes(4, 'little'))
                            block[0] += string_length
                            block[1] -= string_length
                            ptr_strings[bin_string] = string_pointer
                            break
                        elif blocks.index(block) == len(blocks) - 1:
                            print("{} run out of space.".format(file))
                else:
                    binfile.seek(pointer)
                    binfile.write(ptr_strings[bin_string].to_bytes(4, 'little'))
            else:
                for block in blocks:
                    if (string_length := len(bin_string)) <= block[1]:
                        string_offset = block[0]
                        binfile.seek(string_offset)
                        binfile.write(bin_string)
                        block[0] += string_length
                        block[1] -= string_length
                        break
                    elif blocks.index(block) == len(blocks) - 1:
                            print("{} run out of space.".format(file))
    return
