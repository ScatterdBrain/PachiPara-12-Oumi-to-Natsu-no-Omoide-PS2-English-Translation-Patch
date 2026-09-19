import sys
import os
import csv


# target = file
# ptr_offset = RAM offset where file is loaded
# ptr_blocks = list of poiner blocks (offset, size)
# raw_blocks = list of stiring blocks without pointers (offset, size)
targets = {
    "SLPS_255.74" : {
        "ptr_offset" : 0xFFD00,
        "ptr_blocks" : [
            (0x1722B8, 0x418),
            (0x173C90, 0x658),
            (0x181B50, 0x358),
            (0x18F0F8, 0x5E0),
            (0x1949B8, 0x438),
            (0x19DF98, 0x88),
            (0x19FA38, 0x240),
            (0x19FF90, 0x8),
            (0x1A0B60, 0x1E0),
            (0x1A4340, 0x30),
            (0x1A4740, 0x60),
            (0x1A7F38, 0x80),
            (0x1AE4F8, 0x68),
            (0x1B00B8, 0x150),
            (0x1B6900, 0xE0),
            (0x1B72F8, 0x1C8),
            (0x1B8670, 0x28),
            (0x1B8DF8, 0xA0),
            (0x1B99C8, 0x2E0),
            (0x1BAEA0, 0x280),
            (0x1BBB20, 0xA8),
            (0x1BE4F8, 0x958),
            (0x1C17E8, 0x8),
            (0x1C1EA0, 0x2C8),
            (0x1C5C78, 0xE48),
            (0x184820, 0x410)
            ],
        "raw_blocks" : [
            (0x184AF0, 0x30),
            (0x184B30, 0x60),
            (0x1D1600, 0x93),
            (0x1D8120, 0x9),
            (0x1DCE90, 0x70),
            (0x1DD420, 0x460),
            (0x1DD8C0, 0x30),
            (0x1DE150, 0x20),
            (0x1DE195, 0x2B)
            ]
        },
    "M_00_09.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x7919F0, 0x5E90),
            (0x7978C0, 0x90),
            (0x7A2258, 0x168),
            (0x7A2490, 0x1C0),
            (0x7A26C0, 0x80),
            (0x7A6908, 0xC),
            (0x7A6978, 0xC),
            (0x7A69E0, 0x32C),
            (0x7A6D40, 0x160),
            (0x7A7370, 0x14),
            (0x7A73E8, 0x1C),
            (0x7A7460, 0x4C0),
            (0x7A7DA0, 0xD0),
            (0x7A7F84, 0x4C),
            (0x7A93D0, 0x40),
            (0x7AC280, 0x160),
            (0x7AC7C0, 0x27C)
            ],
        "raw_blocks" : [
            (0x7C7570, 0xE0),
            (0x7C90E5, 0x3B),
            (0x7C99C9, 0x53),
            (0x7C9A9C, 0x80),
            (0x7C9E83, 0x7F),
            (0x7CA157, 0x13),
            (0x7CB452, 0x5C),
            (0x7CB780, 0x12),
            (0x7CB7B7, 0x1E),
            (0x7CBB63, 0x75),
            (0x7CBFDC, 0xC4),
            (0x7CC110, 0x36),
            (0x7CC240, 0x40),
            (0x7CC2EE, 0x68),
            (0x7CC3E0, 0xC3)
            ]
        },
    "M_01_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x47CD8, 0x10),
            (0x54E20, 0x2E98),
            (0x6BBD0, 0x3CE0)
            ],
        "raw_blocks" : [
            (0xB2343, 0x92)
            ]
        },
    "M_02_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x627B0, 0x4540),
            (0x76008, 0x2F90)
            ],
        "raw_blocks" : []
        },
    "M_02_02.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x5718, 0x220)
            ],
        "raw_blocks" : []
        },
    "M_03_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x24298, 0x88),
            (0x2D800, 0x2380),
            (0x339E8, 0xE58)
            ],
        "raw_blocks" : []
        },
    "M_04_01.BIN" : {
        "ptr_offset" : 0x473D00,
        "ptr_blocks" : [
            (0x3F90, 0x3F8)
            ],
        "raw_blocks" : []
        },
    "M_CMN.BIN" : {
        "ptr_offset" : 0x38D580,
        "ptr_blocks" : [
            (0x8A3D0, 0x18A0),
            (0x91CD8, 0x16A0),
            (0x99568, 0x1768),
            (0xA0E90, 0x1700),
            (0xA3548, 0x410),
            (0xA8790, 0x1318),
            (0xAA020, 0x30),
            (0xAD3B8, 0xD48),
            (0xAE7E8, 0x208),
            (0xB22B0, 0xB70),
            (0xC4EC8, 0x300),
            (0xCDD18, 0xB00),
            (0xCF878, 0x30),
            (0xCFB88, 0x30),
            (0xCFDF8, 0x28),
            (0xD05A0, 0x150),
            (0xD0C08, 0xB0),
            (0xD0E10, 0x18),
            (0xD3560, 0x960),
            (0xD4E70, 0xC0),
            (0xD62E8, 0x10)
            ],
        "raw_blocks" : [
            (0xDA250, 0x280),
            (0xDAA50, 0x14),
            (0xDAB50, 0xA0),
            (0xDAC20, 0xE),
            (0xDAC70, 0xE),
            (0xDAD70, 0x2236)
            ]
        }
    }


# returns list of lists containing offset to the string, string itself and offset to the pointer of the string
def extract_ptr_strings(infile, ptr_offset : int, ptr_blocks):
    pointer_strings = []
    infile.seek(0, os.SEEK_END)
    file_size = infile.tell()
    for block in ptr_blocks:
        block_strings = []
        for i in range(0, block[1], 4):
            ptr_address = block[0] + i
            infile.seek(ptr_address)
            pointer = int.from_bytes(infile.read(4), 'little')
            if pointer == 0 or pointer <= ptr_offset or pointer >= file_size + ptr_offset:
                continue
            str_address = pointer - ptr_offset
            infile.seek(str_address)
            hex_string = bytearray()
            while byte := infile.read(1):
                if byte == b'\x00':
                    break
                hex_string += byte
            try:
                hex_string = hex_string.decode('shiftjisx0213')
            except:
                hex_string = "Failed to decode."
            if hex_string != "":
                block_strings.append((str_address, hex_string, ptr_address))
        pointer_strings.append(block_strings)
    return pointer_strings


# returns list of lists containing offset to the string, string itself and dummy
def extract_raw_strings(infile, raw_blocks):
    raw_strings = []
    for block in raw_blocks:
        block_strings = []
        pointer = block[0]
        while pointer < block[0] + block[1]:
            infile.seek(pointer)
            str_address = pointer
            hex_string = bytearray()
            while byte := infile.read(1):
                if byte == b'\x00':
                    break
                hex_string += byte
            if hex_string:
                try:
                    hex_string = hex_string.decode('shiftjisx0213')
                except:
                    hex_string = "Failed to decode."
                if hex_string != "":
                    block_strings.append((str_address, hex_string, 0))
            pointer = infile.tell()
        raw_strings.append(block_strings)
    return raw_strings      


def extract_from_file(path):
    if (target := os.path.basename(path)) in targets.keys():
        infile = open(path, 'rb')
        string_list = extract_ptr_strings(infile, targets[target]["ptr_offset"], targets[target]["ptr_blocks"])
        string_list += extract_raw_strings(infile, targets[target]["raw_blocks"])
        infile.close()
        return string_list
    else:
        return False


def main():
    for arg in sys.argv[1:]:
        strings = extract_from_file(arg)
        if not strings:
            break
        with open(arg + ".csv", 'w', encoding='utf-8', newline='') as csvfile:
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
                    writer.writerow([
                        i,
                        ("%X" % string[0]).zfill(8),
                        string[1],
                        "",
                        ("%X" % string[2]).zfill(8) if string[2] != 0 else ""])
    input("Press Any button to close.")


if __name__ == "__main__":
    main()
