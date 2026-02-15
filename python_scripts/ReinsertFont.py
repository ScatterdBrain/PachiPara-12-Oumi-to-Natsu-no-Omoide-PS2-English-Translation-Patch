import sys
import os
from PIL import Image


CHAR_COUNT = 3714
COLUMNS = 32
CHAR_SIZE = 144
WIDTH = 24
HEIGHT= 24
BPP = 2
COLORS = 4
REINSERT_TARGET = "/disc_contents/ROOT.DAT"
FONT_FILE = "/graphics/FONT/FONTALL.DAT.png"
FONT_OFFSET = 720
FONT_DATA_SIZE = 534816


def main(work_dir : str):
    font_path = work_dir + FONT_FILE
    bin_path = work_dir + REINSERT_TARGET
    try:
        image_file = Image.open(font_path, 'r')
    except:
        print("Failed to open " + os.path.abspath(font_path))
        return
    try:
        bin_file = open(bin_path, 'r+b')
    except:
        image_file.close()
        print("Failed to open " + os.path.abspath(bin_path))
        return
    rows = -(-image_file.height // HEIGHT)
    raw_data = bytearray()
    for i in range(rows):
        y = HEIGHT * i
        for j in range(COLUMNS):
            x = WIDTH * j
            char = image_file.crop((x, y, x + WIDTH, y + HEIGHT))
            buffer = char.tobytes()
            for k in range(0, len(buffer), 4):
                raw_data += (buffer[k + 3] << 6 | buffer[k + 2] << 4 | buffer[k + 1] << 2 | buffer[k]).to_bytes(1)
    image_file.close()
    bin_file.seek(FONT_OFFSET)
    bin_file.read(32)
    bin_file.write(raw_data[0:FONT_DATA_SIZE])
    bin_file.close()
    print("Reinserted the font.")
    return


if __name__ == '__main__':
    main()
