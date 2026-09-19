# compression/decompression algorithms for graphics used in pachinko machines

# min/max lengths of data that can be compressed 
MIN_LEN = 4
MAX_LEN = 130
# how far back we can look for repeating bytes
MAX_REF = 512


# decompression algo written from observing assembly code
def pachi_decode(data : bytes, data_offset : int, max_size : int = 0x2000):
    flag = data[data_offset]
    buffer = bytearray()
    pointer = data_offset + 1
    while len(buffer) < max_size and pointer < len(data):
        byte = data[pointer]
        pointer += 1
        if byte != flag:
            buffer += byte.to_bytes(1, 'big')
        else:
            length = data[pointer]
            pointer += 1
            if length == 0:
                buffer += byte.to_bytes(1, 'big')
            else:
                bit = (length & 0x80) >> 7 
                length = length & 0x7F
                offset = data[pointer]
                pointer += 1
                start = len(buffer) - ((offset * 2) + 1 + bit)
                for i in range(length + 3):
                    buffer += buffer[start + i].to_bytes(1, 'big')
    return buffer


# from what i understand, the game is using lz77/78 compression variant.
# as i couldn't find software or code that produces output matching what the game uses
# i wrote this monstrosity... it's slow but it works.
def pachi_encode(data : bytes, flag=None):
    output = bytearray()
    if not flag:
        flag = get_flag(data)
    output += flag
    input_length = len(data)
    pointer = 0
    while pointer <= input_length - MIN_LEN:
        start = pointer - MAX_REF if (pointer - MAX_REF) >= 0 else 0
        end = pointer + MAX_LEN if (pointer + MAX_LEN) <= input_length else input_length
        search_buffer = bytes(data[start:pointer])
        lookahead_buffer = bytes(data[pointer:pointer + MIN_LEN])
        window = search_buffer + lookahead_buffer
        offset = search_for_matches(window, lookahead_buffer)
        if offset > MAX_REF:
            # if there is no match just write the byte and increase pointer by 1
            char = data[pointer].to_bytes(1, 'big')
            pointer += 1
            if char == flag:
                output += flag + (0).to_bytes(1, 'big')
            else:
                output += char
        else:
            # else keep searching for biggest possible match
            offset = offset - ((pointer - start) - 1)
            length = len(lookahead_buffer)
            for i in range(MIN_LEN + 1, MAX_LEN + 1, 1):
                lookahead_buffer = bytes(data[pointer:pointer+i])
                window = search_buffer + lookahead_buffer
                tmp_offset = search_for_matches(window, lookahead_buffer)
                if tmp_offset > MAX_REF:
                    break
                else:
                    offset = tmp_offset - ((pointer - start) - 1)
                    length = len(lookahead_buffer)
            pointer += length
            offset = -offset
            bit = 0
            # extra bit if offset is even number
            if (offset % 2) != 0: 
                bit = 0x80
            offset = (offset // 2).to_bytes(1, 'big')
            length = ((length - 3) | bit).to_bytes(1, 'big')
            output += flag + length + offset
    # write leftovers
    while pointer < input_length:
        char = data[pointer].to_bytes(1, 'big')
        pointer += 1
        if char == flag:
            output += flag + (0).to_bytes(1, 'big')
        else:
            output += char
    return output


def get_flag(data : bytes):
    # count how many times each byte appears in the file and use least used one as the flag for compressed data
    # original files never use value above 0x80 so i won't use them aswell, however it shouldn't really matter
    use_count = [0] * 256
    for i in range(len(data)):
        use_count[data[i]] += 1
    flag = 0x80
    for i in range(1, 128):
        if use_count[i] < flag:
            flag = use_count[i]
    try:
        return use_count.index(flag).to_bytes(1, 'big')
    except:
        return (flag).to_bytes(1, 'big')


def search_for_matches(window : bytes, buffer : bytes):
    # starting from the end of larger array we search for a matching smaller array then get its offset
    # if no matches are found, return value that breaks the loop
    length = len(buffer)
    for i in range(len(window) - 1, 0, -1):
        if buffer == window[i - length : i]:
            return i - length
    return MAX_REF + 1
