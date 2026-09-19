import zlib

# PNG specifications https://www.w3.org/TR/PNG-Introduction.html
# functions to help encode bitmap data as png

PNG_SIGNATURE = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
IHDR = b'\x49\x48\x44\x52'
PLTE = b'\x50\x4C\x54\x45'
TRNS = b'\x74\x52\x4E\x53'
TEXT = b'\x74\x45\x58\x74'
IDAT = b'\x49\x44\x41\x54'
IEND = b'\x49\x45\x4E\x44'


def buffer_to_chunk(buffer : bytearray, chunk_type : str):
    chunk = bytearray()
    chunk += len(buffer).to_bytes(4, 'big')
    chunk += chunk_type + buffer + zlib.crc32(chunk_type + buffer).to_bytes(4, 'big')
    return chunk


def write_ihdr(png_data : bytearray, width : int, height : int, bpp : int, color_type : int):
    buffer = bytearray()
    buffer += (width).to_bytes(4, 'big')
    buffer += (height).to_bytes(4, 'big')
    buffer += (bpp).to_bytes(1, 'big')
    buffer += (color_type).to_bytes(1, 'big')
    buffer += (0).to_bytes(3, 'big')
    png_data += buffer_to_chunk(buffer, IHDR)
    return


def write_plte(png_data : bytearray, color_data : bytearray):
    buffer = bytearray()
    for i in range(0, len(color_data), 4):
        buffer += color_data[i:i + 3]
    png_data += buffer_to_chunk(buffer, PLTE)
    return


def write_trns(png_data : bytearray, color_data : bytearray):
    buffer = bytearray()
    for i in range(0, len(color_data), 4):
        buffer += color_data[i + 3].to_bytes(1, 'big')
    png_data += buffer_to_chunk(buffer, TRNS)
    return


def write_text(png_data : bytearray, keyword : str, string : str):
    buffer = bytearray()
    buffer += bytearray(keyword, 'ascii') + (0).to_bytes(1, 'big')
    buffer += bytearray(string, 'ascii')
    png_data += buffer_to_chunk(buffer, TEXT)
    return


def write_idat(png_data : bytearray, compressed_data : bytearray, buffer_size : int = 0):
    pointer = 0
    loop = True
    if buffer_size <= 0:
        buffer_size = len(compressed_data)
    while loop:
        if pointer + buffer_size >= len(compressed_data):
            buffer = compressed_data[pointer:]
            loop = False
        else:
            buffer = compressed_data[pointer:pointer + buffer_size]
        pointer += buffer_size
        png_data += buffer_to_chunk(buffer, IDAT)
    return


def write_iend(png_data : bytearray):
    png_data += (0).to_bytes(4, 'big')
    png_data += IEND + zlib.crc32(IEND).to_bytes(4, 'big')
    return


def filter_pixel_data(pixel_data : bytearray, width : int, bpp : int):
    filtered_pixel_data = bytearray()
    scanline = bpp * width // 8
    for i in range(0, len(pixel_data), scanline):
        filtered_pixel_data += (0).to_bytes(1, 'big') + pixel_data[i: i + scanline]
    return filtered_pixel_data


def compress_pixel_data(pixel_data : bytearray, level : int = 6, wbits : int = 15):
    return zlib.compress(pixel_data, level = level, wbits = wbits)
