import sys
import os
import csv


# WIP text reinsertion script
reinsertion_targets = {
    "M_01_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 294032, "size" : 71},
            2 : {"offset" : 294128, "size" : 53551},
            3 : {"offset" : 370784, "size" : 70511}
            # 4 {"offset" : 729923, "size" : 136} pointers for text in this block loaded through code. Ex. lui a0,0x1234; addiu a0,a0,0x5678;
            # TODO work on reinsertion of "pointerless" text.
            }
        },
    "M_02_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 323760, "size" : 79615},
            2 : {"offset" : 421104, "size" : 62231}
            }
        },
    "M_02_02.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 19288, "size" : 3007}
            }
        },
    "M_03_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 147744, "size" : 375},
            2 : {"offset" : 148256, "size" : 38111},
            3 : {"offset" : 195456, "size" : 15975}
            }
        },
    "M_04_01.BIN" : {
        "pointer_offset" : 4668672, "text_blocks" : {
            1 : {"offset" : 13120, "size" : 3151}
            }
        },
    "M_CMN.BIN" : {
        "pointer_offset" : 3724672, "text_blocks" : {
            1 : {"offset" : 541568, "size" : 24655},
            2 : {"offset" : 573864, "size" : 23343},
            3 : {"offset" : 604008, "size" : 24063},
            4 : {"offset" : 635336, "size" : 23751},
            5 : {"offset" : 665640, "size" : 3359},
            6 : {"offset" : 670040, "size" : 20023},
            7 : {"offset" : 696192, "size" : 159},
            8 : {"offset" : 696400, "size" : 13159},
            9 : {"offset" : 713504, "size" : 1223},
            10 : {"offset" : 715248, "size" : 14527},
            11 : {"offset" : 802384, "size" : 4215},
            12 : {"offset" : 821424, "size" : 21607},
            13 : {"offset" : 849840, "size" : 199},
            14 : {"offset" : 850688, "size" : 135},
            15 : {"offset" : 851360, "size" : 87},
            16 : {"offset" : 852128, "size" : 1279},
            17 : {"offset" : 854360, "size" : 687},
            18 : {"offset" : 855520, "size" : 47},
            19 : {"offset" : 855856, "size" : 9775},
            20 : {"offset" : 871656, "size" : 391}
            # 21 : {"offset" : 893520, "size" : 639},
            # 22 : {"offset" : 895568, "size" : 191},
            # 23 : {"offset" : 895824, "size" : 175},
            # 24 : {"offset" : 896032, "size" : 47},
            # 25 : {"offset" : 896112, "size" : 47},
            # 26 : {"offset" : 905126, "size" : 25}
            }
        },
    "SLPS_255.74" : {
        "pointer_offset" : 1047808, "text_blocks" : {
            1 : {"offset" : 1512256, "size" : 3959},
            2 : {"offset" : 1517264, "size" : 5567},
            3 : {"offset" : 1576480, "size" : 3375},
            # 4 : {"offset" : 1592048, "size" : 47},
            # 5 : {"offset" : 1592112, "size" : 95},
            6 : {"offset" : 1622144, "size" : 12407},
            7 : {"offset" : 1654336, "size" : 2935},
            8 : {"offset" : 1695088, "size" : 551},
            9 : {"offset" : 1698552, "size" : 3903},
            10 : {"offset" : 1703792, "size" : 31},
            11 : {"offset" : 1704976, "size" : 1871},
            12 : {"offset" : 1721072, "size" : 79},
            13 : {"offset" : 1721984, "size" : 191},
            14 : {"offset" : 1736168, "size" : 335},
            15 : {"offset" : 1762016, "size" : 535},
            16 : {"offset" : 1767936, "size" : 1719},
            17 : {"offset" : 1794928, "size" : 1423},
            18 : {"offset" : 1796576, "size" : 2327},
            19 : {"offset" : 1803712, "size" : 175},
            20 : {"offset" : 1805112, "size" : 703},
            21 : {"offset" : 1806416, "size" : 2423},
            22 : {"offset" : 1809576, "size" : 4599},
            23 : {"offset" : 1817208, "size" : 167},
            24 : {"offset" : 1817640, "size" : 10447},
            25 : {"offset" : 1841056, "size" : 71},
            26 : {"offset" : 1841224, "size" : 1623},
            27 : {"offset" : 1845232, "size" : 13447}
            # 28 : {"offset" : 1906176, "size" : 147},
            # 29 : {"offset" : 1933600, "size" : 2358},
            # 30 : {"offset" : 1953424, "size" : 95},
            # 31 : {"offset" : 1954848, "size" : 1119},
            # 32 : {"offset" : 1956032, "size" : 47},
            # 33 : {"offset" : 1958224, "size" : 31},
            # 34 : {"offset" : 1958293, "size" : 42}
            }
        }
    # "M_00_09.BIN" : {
        # "pointer_offset" : 4668672, "text_blocks" : {
            # 1 : {"offset" : 8156528, "size" : 7711},
            # 2 : {"offset" : 8164896, "size" : 2895},
            # 3 : {"offset" : 8168656, "size" : 3071},
            # 4 {"offset" : 8172128, "size" : 863},
            # 5 {"offset" : 8173440, "size" : 1119},
            # 6 {"offset" : 8174624, "size" : 1151},
            # 7 {"offset" : 8175888, "size" : 927},
            # 8 {"offset" : 8177168, "size" : 5183}
            # }
        # }
    }


def main():
    work_dir = os.getcwd()
    if os.path.normpath(work_dir).split(os.path.sep)[-1] != "python_scripts":
        input('Press Enter to close.')
        sys.exit()
    work_dir = os.path.dirname(work_dir)
    for target in reinsertion_targets.keys():
        match target:
            case "SLPS_255.74":
                bin_path = work_dir + "/assets/" + target
                csv_path =  work_dir + "/text/" + target + ".csv"
            case _:
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
                if row["block"] == "_":
                    continue
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
                    # Instead of reinserting repeated strings, point to a single string.
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
    
