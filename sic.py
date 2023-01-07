from atexit import register


OPTAB = {
    # SIC Instruction Set
    "ADD":  0x18,
    "AND":  0x40,
    "COMP": 0x28,
    "DIV":  0x24,
    "J":    0x3C,
    "JEQ":  0x30,
    "JGT":  0x34,
    "JLT":  0x38,
    "JSUB": 0x48,
    "LDA":  0x00,
    "LDCH": 0x50,
    "LDL":  0x08,
    "LDX":  0x04,
    "MUL":  0x20,
    "OR":   0x44,
    "RD":   0xD8,
    "RSUB": 0x4C,
    "STA":  0x0C,
    "STCH": 0x54,
    "STL":  0x14,
    "STSW": 0xE8,
    "STX":  0x10,
    "SUB":  0x1C,
    "TD":   0xE0,
    "TIX":  0x2C,
    "WD":   0xDC,
    # SIC/XE Intruction Set (blue)
    "ADDR": 0x90,
    "CLEAR": 0xB4,
    "COMPR": 0xA0,
    "DIVR": 0x9C,
    "LDB":  0x68,
    "LDS":  0x6C,
    "LDT":  0x74,
    "MULR": 0x98,
    "RMO":  0xAC,
    "SHIFTL": 0xA4,
    "SHIFTR": 0xA8,
    "STB": 0x78,
    "STS": 0x7C,
    "STT": 0x84,
    "SUBR": 0x94,
    "TIXR": 0xB8,
}

# FORMAT1 都是紅字(不支援)
FORMAT2 = ["ADDR", "CLEAR", "COMPR", "DIVR", "MULR",
           "RMO", "SHIFTL", "SHIFTR", "SUBR", "TIXR"]
# FORMAT3_and_4 = [] 因為FORMAT1不支援，所以不是2就是3or4

DIRECTIVE = [
    "START",
    "END",
    "WORD",
    "BYTE",
    "RESW",
    "RESB",
    # SIC/XE
    'BASE',
]


SICXE_REGISTER = {
    "A": 0,
    "X": 1,
    "L": 2,
    "PC": 8,
    "SW": 9,
    # sic/xe
    "B": 3,
    "S": 4,
    "T": 5,
    "F": 6,
}


def isDirective(token):
    if token in DIRECTIVE:
        return True
    else:
        return False


def isInstruction(token):
    if token in OPTAB:
        return True
    else:
        return False


def find_format(op):
    if op in FORMAT2:
        return "FORMAT2"
    elif isInstruction(op):
        return "FORMAT3or4"
