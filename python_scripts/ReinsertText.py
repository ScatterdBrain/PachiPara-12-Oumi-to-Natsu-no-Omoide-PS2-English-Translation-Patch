import sys
import os
import csv


# WIP text reinsertion script
# TODO add the rest of the files
reinsertion_targets = {
    "M_01_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 294032, "size" : 71},
            2 : {"offset" : 294128, "size" : 53551},
            3 : {"offset" : 370784, "size" : 70511},
            # 4 {"offset" : 729923, "size" : 136} pointers for text in this block loaded through code. Ex. lui a0,0x1234; addiu a0,a0,0x5678;
            # TODO work on reinsertion of "pointerless" text.
            }
        },
    "M_02_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 323760, "size" : 79615},
            2 : {"offset" : 421104, "size" : 62231}
            }
        }  
    }
pointer_offsets = {
    "M_00_09.BIN" : 4668672,
    "M_01_01.BIN" : 4668672,
    "M_02_01.BIN" : 4668672,
    "M_02_02.BIN" : 4668672,
    "M_03_01.BIN" : 4668672,
    "M_04_01.BIN" : 4668672,
    "M_CMN.BIN" : 3724672,
    "SLPS_255.74" : 1047808
    }


def main():
    work_dir = os.getcwd()
    if os.path.normpath(work_dir).split(os.path.sep)[-1] != "python_scripts":
        input('Press Enter to close.')
        sys.exit()
    work_dir = os.path.dirname(work_dir)
    for target in reinsertion_targets.keys():
        bin_path = work_dir + "/assets/MAP/" + target
        csv_path =  work_dir + "/text/" + target.rsplit('.', 1)[0] + ".csv"
        if not os.path.isfile(bin_path):
            print(bin_path + " is missing.")
            continue
        if not os.path.isfile(csv_path):
            print(csv_path + " is missing.")
            continue
        text_blocks = {}
        with open(csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter = ';', quotechar = '"')
            for row in reader:
                if row["block"] not in text_blocks.keys():
                    text_blocks[row["block"]] = {}
                if row["pointer"] != "":
                    if row["e_string"] != "":
                        text_blocks[row["block"]][int(row["pointer"], 16)] = row["e_string"]
                    else:
                        text_blocks[row["block"]][int(row["pointer"], 16)] = row["j_string"]
        with open(bin_path, 'r+b') as binfile:
            free_space = {}
            excess_strings = {}
            for block in reinsertion_targets[target]["text_blocks"]:
                offset = reinsertion_targets[target]["text_blocks"][block]["offset"]
                size = reinsertion_targets[target]["text_blocks"][block]["size"]
                binfile.seek(offset)
                binfile.write(bytearray(size))
                string_offset = offset
                string_boundry = size + offset
                data = {}
                repeats = 0
                for pointer in text_blocks[str(block)]:
                    bin_string = bytearray()
                    try:
                        bin_string = text_blocks[str(block)][pointer].encode(encoding='shift-jis')
                    except:
                        # Workaround for some of the characters the game is using in original strings. Shouldn't matter if all strings are translated.
                        bin_string = (target + "_" + ("%X" % pointer)).encode(encoding='shift-jis')
                    bin_string += b'\x00'
                    if string_offset > string_boundry:
                        excess_strings[bin_string] = pointer
                        continue
                    if bin_string not in data.keys():
                        data[bin_string] = {"offset" : string_offset, "pointer" : pointer}
                        string_offset += len(bin_string)
                    elif bin_string in data.keys():
                        data[repeats] = {"offset" : data[bin_string]["offset"], "pointer" : pointer}
                        repeats += 1
                if string_boundry - string_offset > 16:
                    free_space[block] = {"offset" : string_offset, "size" : string_boundry - string_offset}
                for key in data:
                    if type(key) is bytes:
                        binfile.seek(data[key]["offset"])
                        binfile.write(key)
                    binfile.seek(data[key]["pointer"])
                    binfile.write((data[key]["offset"] + reinsertion_targets[target]["pointer_offset"]).to_bytes(4, byteorder='little', signed=True))
            # TODO handle excess strings
    input('Press Enter to close.')
    sys.exit()
    

if __name__ == "__main__":
    main()
