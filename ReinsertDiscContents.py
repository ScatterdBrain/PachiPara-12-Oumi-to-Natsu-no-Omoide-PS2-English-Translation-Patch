import sys


ISO_PATH = "PachiPara12_[SLPS-25574].iso"
DISC_CONTENTS = {
    "SLPS_255.74" : 1245796352,
    "ROOT.DAT" : 1491707904,
    "COMMON.DAT" : 1428211712,
    "DATA/MAP/M_00_09.DAT" : 1247758336,
    "DATA/MAP/M_01_01.DAT" : 1256781824,
    "MAP/M_00_09.BIN" : 1416519680,
    "MAP/M_01_01.BIN" : 1424703488,
    "MAP/M_02_01.BIN" : 1425483776,
    "MAP/M_02_02.BIN" : 1426337792,
    "MAP/M_03_01.BIN" : 1426397184,
    "MAP/M_04_01.BIN" : 1427070976,
    "MAP/M_CMN.BIN" : 1427140608
    # "MPEG/A01.pss" : 663552,
    # "MPEG/B01.pss" : 44247040,
    # "MPEG/C01.pss" : 82669568
    }


iso_file = open(ISO_PATH, 'r+b')
for key in DISC_CONTENTS.keys():
    with open("disc_contents/" + key, 'rb') as infile:
        iso_file.seek(DISC_CONTENTS[key])
        iso_file.write(infile.read())
iso_file.close()
input("Press Enter to close.")
sys.exit()
