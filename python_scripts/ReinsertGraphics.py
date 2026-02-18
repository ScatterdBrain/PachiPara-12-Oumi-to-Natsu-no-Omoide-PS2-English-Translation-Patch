import sys
import os
from PIL import Image # github.com/python-pillow/Pillow
import imagequant # github.com/wanadev/imagequant-python


# TM2 specifications from https://openkh.dev/common/tm2.html
REINSERT_TARGETS = {
    "COMMON.DAT" : {
        "03041.TM2" : 35403776,
        "03051.TM2" : 35770368,
        "03052.TM2" : 35938304,
        "03053.TM2" : 36141056,
        "03055.TM2" : 36274176,
        "03056.TM2" : 36407296,
        "03057.TM2" : 36575232,
        "03131.TM2" : 44023808
        },
    "ROOT.DAT" : {
        "03045.TM2" : 573184
        }
    }


def main(work_dir : str):
    for target in REINSERT_TARGETS.keys():
        match target:
            case "M_00_09.DAT" | "M_01_01.DAT":
                dat_path = work_dir + "/disc_contents/DATA/MAP/" + target
            case _:
                dat_path = work_dir + "/disc_contents/" + target
        try:
            dat_file = open(dat_path, 'r+b')
        except:
            print("Failed to open " + os.path.abspath(dat_path))
            continue
        graphics_path = work_dir + "/graphics/" + target.rsplit('.', 1)[0] + "/"
        graphics_list = os.listdir(graphics_path)
        for item in graphics_list:
            if item.rsplit('.', 1)[-1] == "png" and item.rsplit('.', 1)[0] in REINSERT_TARGETS[target].keys():
                dat_file.seek(REINSERT_TARGETS[target][item.rsplit('.', 1)[0]])
                dat_file.read(20)
                palette_size = int.from_bytes(dat_file.read(4), byteorder='little', signed=False)
                bitmap_size = int.from_bytes(dat_file.read(4), byteorder='little', signed=False)
                dat_file.read(7)
                match int.from_bytes(dat_file.read(1), signed=False):
                    case 3:
                        bpp = 32
                    case 4:
                        bpp = 4
                    case 5:
                        bpp = 8
                    case _:
                        print(graphics_path + item + " not supported.")
                        continue
                png_image = Image.open(graphics_path + item, 'r')
                mode = "RGBA"
                match bpp:
                    case 32:
                        color_number = 65536
                    case 8:
                        color_number = 256
                    case 4:
                        color_number = 16
                tm2_image = imagequant.quantize_pil_image(png_image, dithering_level = 0.0, max_colors = color_number, min_quality = 0, max_quality = 100)
                png_image.close()
                tm2_image = tm2_image.convert(mode = mode, palette = Image.Palette.ADAPTIVE, colors = color_number)  
                pixel_data = bytearray(tm2_image.tobytes())
                # Fix transparanceis
                for i in range(0, len(pixel_data), 4):
                    if pixel_data[i + 3] > 0:
                        pixel_data[i + 3] = (pixel_data[i + 3] >> 1) + 1
                # Create palette if needed
                match bpp:
                    case 8:
                        temp = []
                        new_pixel_data = bytearray()
                        for i in range(0, len(pixel_data), 4):
                            a = pixel_data[i:i + 4][-1]
                            if a != 0:
                                r = pixel_data[i:i + 4][0]
                                g = pixel_data[i:i + 4][1]
                                b = pixel_data[i:i + 4][2]
                            else:
                                r = 0
                                g = 0
                                b = 0
                            pixel = bytes([r, g, b, a])
                            if pixel not in temp:
                                temp.append(pixel)
                            new_pixel_data += (temp.index(pixel).to_bytes())
                            # Padding
                        while True:
                            if len(temp) < 256:
                                temp.append(bytes(b'\x00\x00\x00\x00'))
                            else:
                                break
                        color_data = bytearray()
                        for value in temp:
                            color_data += value
                        del temp
                        # Swizzle palette
                        sorted_palette = bytearray()
                        for i in range(0, 1024, 128):
                            chunk_1 = color_data[i:i + 32]
                            chunk_2 = color_data[i + 32:i + 64]
                            chunk_3 = color_data[i + 64:i + 96]
                            chunk_4 = color_data[i + 96:i + 128]
                            sorted_palette += chunk_1 + chunk_3 + chunk_2 + chunk_4
                        color_data = sorted_palette
                        del sorted_palette
                        pixel_data = new_pixel_data
                        del new_pixel_data
                    case 4:
                        temp = []
                        new_pixel_data = bytearray()
                        counter = 0
                        for i in range(0, len(pixel_data), 4):
                            a = pixel_data[i:i + 4][-1]
                            if a != 0:
                                r = pixel_data[i:i + 4][0]
                                g = pixel_data[i:i + 4][1]
                                b = pixel_data[i:i + 4][2]
                            else:
                                r = 0
                                g = 0
                                b = 0
                            pixel = bytes([r, g, b, a])
                            if pixel not in temp:
                                temp.append(pixel)
                            if counter == 0:
                                counter = temp.index(pixel).to_bytes().hex()[1]
                            elif counter != 0:
                                counter = temp.index(pixel).to_bytes().hex()[1] + counter
                                new_pixel_data += (bytes.fromhex(counter))
                                counter = 0
                        # Padding
                        while True:
                            if len(temp) < 16:
                                temp.append(bytes(b'\x00\x00\x00\x00'))
                            else:
                                break
                        color_data = bytearray()
                        for value in temp:
                            color_data += value
                        del temp
                        pixel_data = new_pixel_data
                        del new_pixel_data
                    case _:
                        pass
                # For now just overwrite existing data so there is no need to rebuild archives
                if len(pixel_data) == bitmap_size:
                    xy = tm2_image.size
                    dat_file.write(xy[0].to_bytes(2, byteorder='little', signed=False))
                    dat_file.write(xy[1].to_bytes(2, byteorder='little', signed=False))
                    dat_file.read(24)
                    dat_file.write(pixel_data)
                    dat_file.write(color_data)
                    print(graphics_path + item + " reinserted.")
                else:
                    print(graphics_path + item + " wrong bitmap size.")
        print(target + " done.")


if __name__ == '__main__':
    main()
