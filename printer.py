from read_bdf import characters
# import characters
import string
import time
import math
import serial
import adafruit_thermal_printer
import qrcode

# for n in range(0, 2000):
#     index = 23*math.sin(n/100)+24
#     print("index: {}, n: {}".format(index, n))
#     byte_index = math.floor(index)

#     bit_index = 7-math.floor((index - byte_index)*8)

#     print((byte_index, bit_index))
#     out = bytearray(48)
#     out[byte_index] = 2**bit_index

#     out = b'\x12*\x01\x30'+out
#     print(out)
#     uart.write(out)
#     time.sleep(1)


def chunks(input, n):
    out = []
    i = 0
    j = n
    while i < len(input):
        if j > len(input):
            out.append(input[i:])
        else:
            out.append(input[i:j])
        i += n
        j += n
    return out


def print_array_of_bytes(uart, data):
    for n in range(0, len(data)):
        out = bytearray(b'\x12*') + bytearray([1, len(data[n])]) + data[n]
        # print(out)
        uart.write(out)
        time.sleep(0.1)


def bits_to_bytes(bits, bit_order_forward=True):
    out = bytearray((len(bits)+7)//8)
    chunked = chunks(bits, 8)

    def bit_mapping(bit_index, value):
        if bit_order_forward:
            # print(value, bit_index)
            return value*2**(bit_index)
        else:
            return value*2**(7-bit_index)

    for byte_index, bits_for_this_byte in enumerate(chunked):
        # print(byte_index, bits_for_this_byte)
        this_byte = 0
        for bit_index, bit_value in enumerate(bits_for_this_byte):
            this_byte += bit_mapping(bit_index, bit_value)
        out[byte_index] = this_byte
    return out


def _2d_bitarray_to_array_of_bytes(data, scale=1):
    return [bits_to_bytes(
        line, False) for line in scale_xy(data, scale=scale)]


def print_2d_bitarray(uart, data, scale=1):
    print_array_of_bytes(uart, _2d_bitarray_to_array_of_bytes(data))


def scale_x(bits, scale=1):
    out = []
    for bit in bytearray(bits):
        out.extend([bit]*scale)
    return out


def scale_xy(bits, scale=1):
    if scale == 1:
        return bits
    out = []
    for line in bits:
        scaled_line = scale_x(line, scale)
        out.extend([scaled_line]*scale)
    return out


def side_by_side(leftA, rightA, extend=False):
    if extend:
        max_height = max(len(leftA), len(rightA))
        if len(leftA) != max_height:
            leftA = center_bitmap_height(leftA, max_height)
        if len(rightA) != max_height:
            rightA = center_bitmap_height(rightA, max_height)

    return [left+right for left, right in zip(leftA, rightA)]


def center_bitmap_height(bitmap, height):
    added_height = height - len(bitmap)
    if added_height < 0:
        raise Exception("height must be greater than bitmap height")
    out = [b""]*(added_height//2)
    out.extend(bitmap)
    out.extend([b""]*(added_height//2 + added_height % 2))
    return out


_char_to_bitmap_key = {
    ' ': 'space',
    '!': 'exclam',
    '"': 'quotedbl',
    '#': 'numbersign',
    '$': 'dollar',
    '%': 'percent',
    '&': 'ampersand',
    "'": 'quotesingle',
    '(': 'parenleft',
    ')': 'parenright',
    '*': 'asterisk',
    '+': 'plus',
    ',': 'comma',
    '-': 'hyphen',
    '.': 'period',
    '/': 'slash',
    '0': 'zero',
    '1': 'one',
    '2': 'two',
    '3': 'three',
    '4': 'four',
    '5': 'five',
    '6': 'six',
    '7': 'seven',
    '8': 'eight',
    '9': 'nine',
    ':': 'colon',
    ';': 'semicolon',
    '<': 'less',
    '=': 'equal',
    '>': 'greater',
    '?': 'question',
    '@': 'at',
    'A': 'A',
    'B': 'B',
    'C': 'C',
    'D': 'D',
    'E': 'E',
    'F': 'F',
    'G': 'G',
    'H': 'H',
    'I': 'I',
    'J': 'J',
    'K': 'K',
    'L': 'L',
    'M': 'M',
    'N': 'N',
    'O': 'O',
    'P': 'P',
    'Q': 'Q',
    'R': 'R',
    'S': 'S',
    'T': 'T',
    'U': 'U',
    'V': 'V',
    'W': 'W',
    'X': 'X',
    'Y': 'Y',
    'Z': 'Z',
    '[': 'bracketleft',
    '\\': 'backslash',
    ']': 'bracketright',
    '^': 'asciicircum',
    '_': 'underscore',
    '`': 'grave',
    'a': 'a',
    'b': 'b',
    'c': 'c',
    'd': 'd',
    'e': 'e',
    'f': 'f',
    'g': 'g',
    'h': 'h',
    'i': 'i',
    'j': 'j',
    'k': 'k',
    'l': 'l',
    'm': 'm',
    'n': 'n',
    'o': 'o',
    'p': 'p',
    'q': 'q',
    'r': 'r',
    's': 's',
    't': 't',
    'u': 'u',
    'v': 'v',
    'w': 'w',
    'x': 'x',
    'y': 'y',
    'z': 'z',
    '{': 'braceleft',
    '|': 'bar',
    '}': 'braceright',
    '~': 'asciitilde',
}


def string_characters(chars):
    out = []
    for char in chars:
        out = side_by_side(
            out, characters[_char_to_bitmap_key[char]], extend=True)
    return out


def print_code(code, printer_port):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
    qr.add_data(code)

    qrdata = _2d_bitarray_to_array_of_bytes(qr.get_matrix(), scale=3)

    uart = serial.Serial(printer_port, 19200)

    ThermalPrinter = adafruit_thermal_printer.get_printer_class(3)
    printer = ThermalPrinter(uart, auto_warm_up=False)

    print_array_of_bytes(uart, side_by_side(
        qrdata, center_bitmap_height(string_characters(code), len(qrdata))))

    printer.feed(2)
    uart.close()
