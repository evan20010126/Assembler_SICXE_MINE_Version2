from ast import operator
from email.mime import base
from lib2to3.pgen2.token import PLUS
from lib2to3.pytree import Base
import sys

from numpy import disp

import sic
import sicasmparser

import objfile


def processBYTEC(operand):
    constant = ""
    for i in range(2, len(operand)-1):
        tmp = hex(ord(operand[i]))
        tmp = tmp[2:]
        if len(tmp) == 1:
            tmp = "0" + tmp
        tmp = tmp.upper()
        constant += tmp
    return constant


def generateInstruction(opcode, operand, SYMTAB):  # opcode 不為假指令，主程式有判斷過了
    global M_record_buffer
    global LOCCTR
    global Base_register

    if t[1][0] == "+" and sic.find_format(t[1][1:]) == "FORMAT3or4":
        op_format = 4  # is format4
    elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT3or4":
        op_format = 3  # is format3
    elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT2":
        op_format = 2
    else:
        op_format = 1
        print("opcode not find, so it's format 1.")

    # 會自依照format把opcode推到高位元
    if t[1][0] == "+":
        instruction = int(sic.OPTAB[opcode[1:]] * (2**(8*(op_format-1))))
    else:
        instruction = int(sic.OPTAB[opcode] * (2**(8*(op_format-1))))

    # 先處理 format2
    if op_format == 2:
        operand_split = operand.split(',')
        if (len(operand_split) == 1):
            instruction += sic.SICXE_REGISTER[operand_split[0]] * (2**4)
        elif (len(operand_split) == 2):
            instruction += sic.SICXE_REGISTER[operand_split[0]] * (2**4)
            instruction += sic.SICXE_REGISTER[operand_split[1]]
        # print(objfile.hexstrToWord(hex(instruction)))  # format2 僅有4bit 老師的function會補成6bit
        return objfile.hexstrToWord(hex(instruction))[2:]

    # 處理 format3 and format4 的情形
    if operand != None:
        # 先設定 n and i bit
        if operand[0] == '@':
            if op_format == 3:
                instruction += 2**17
            if op_format == 4:
                instruction += 2**25

            operand = operand[1:]
        elif operand[0] == '#':
            if op_format == 3:
                instruction += 2**16
            if op_format == 4:
                instruction += 2**24

            operand = operand[1:]
        else:   # 如果不是@與# 且為SIC/XE編譯出來的機器碼 填11
            if op_format == 3:
                instruction += 2**17
                instruction += 2**16
            if op_format == 4:
                instruction += 2**25
                instruction += 2**24

        # 再設定 x bit
        if operand[len(operand)-2:] == ',X':
            if op_format == 3:
                instruction += 32768  # 32768 = 2**15
            if op_format == 4:
                instruction += 2**23
            operand = operand[:len(operand)-2]

        # 再設定 b p
        if operand not in SYMTAB:  # 是數字 設定b p bit都是0
            if op_format == 3:
                pass
            if op_format == 4:
                pass
        else:   # 判斷要 base relative or pc relative 也可以算disp
            next_locctr = LOCCTR + op_format    # 因為老師的檔案是後面才加 locctr

            if (op_format == 4):
                # b, p =0
                disp = SYMTAB[operand]
            elif (op_format == 3):
                if (SYMTAB[operand] - next_locctr) <= 2047 and (SYMTAB[operand] - next_locctr) >= -2048:
                    # PC relative
                    # compute disp 有二補數的問題
                    instruction += 2**13  # set p = 1
                    if (SYMTAB[operand] - next_locctr) < 0:
                        disp = (abs(SYMTAB[operand] - next_locctr)
                                ^ 0b111111111111) + 0b1
                    else:
                        disp = (SYMTAB[operand] - next_locctr)

                elif (SYMTAB[operand] - Base_register) <= 4095 and (SYMTAB[operand] - Base_register) >= 0:
                    # Base relative
                    instruction += 2**14  # set b = 1
                    disp = (SYMTAB[operand] - Base_register)
                    # Debug 用
                    # if opcode == "STCH" and operand == "BUFFER":
                    #     print(Base_register)
                else:
                    print("You need to use format 4. Variable disp will not be assign!")
                    print(opcode)
                    print(Base_register)

        # 再設定 e (Why 不在一開始分類format就設定-> 因為format2不會有e)
        if op_format == 3:
            pass
            # instruction += (2**12) # set e=0
        elif op_format == 4:
            instruction += (2**20)

        # 最後設定 disp
        if operand not in SYMTAB:  # 處理像立即值後面接數字 Ex. #3
            instruction += int(operand)  # 經過測試是可以這樣: int("1110") -> 1110
        elif op_format == 3 or op_format == 4:
            instruction += disp  # set b, p 時算出來的

        if op_format == 4 and (operand in SYMTAB):
            M_record_buffer.append(LOCCTR)

        #! 特殊情況
        # 若有 LDB指令(存入Base暫存器)，紀錄Base暫存器的值，以供後續disp計算用
        # 假設 LDB 後 operand 僅有立即值的情況，因網路上沒有仔細講LDB後可放什麼，而若用@來放值進去base，由assembler的角度沒有辦法知道Base暫存器的值
        if opcode == "LDB" or opcode == "+LDB":
            if operand in SYMTAB:
                Base_register = int(SYMTAB[operand])
            else:  # 為常數
                Base_register = int(operand)
    else:
        # no operand 像是RSUB，而SIC/xe編譯出來的指令必須n i = 1
        if op_format == 3:
            instruction += 2**17
            instruction += 2**16
        if op_format == 4:
            instruction += 2**25
            instruction += 2**24
    '''
    下面的程式碼若把 if & else 都拿掉
    最後僅剩下最後一行"return objfile.hexstrToWord(hex(instruction))"
    然後跑midterm.asm就可以發現 F103026 少一個0的問題
    '''
    if (len(objfile.hexstrToWord(hex(instruction))) != op_format*8//4):
        # 使用段考考題測試，若是opcode + n i 之後仍為16以下的數字(這樣只有1bit)，會沒有補0，因為老師的hexstrToWord套用後僅會補齊到6個字母 Ex. F103026 是 Format3 但少一個數字 原因是因為第一個byte用16進制表示僅有一個字母
        empty_space = op_format*8//4 - \
            len(objfile.hexstrToWord(hex(instruction)))
        output_str = objfile.hexstrToWord(hex(instruction))
        for i in range(0, empty_space):
            output_str = "0" + output_str
        return output_str
    else:
        return objfile.hexstrToWord(hex(instruction))


if len(sys.argv) != 2:
    print("Usage: python3 assembler.py <source file>")
    sys.exit()

lines = sicasmparser.readfile(sys.argv[1])

SYMTAB = {}

# PASS 1
for line in lines:
    t = sicasmparser.decompositLine(line)  # t 為切割過的程式碼(tuple)

    if t == (None, None, None):
        continue

    if t[1] == "START":
        STARTING = int(t[2], 16)  # 把start放進去 且 base = 16
        LOCCTR = int(STARTING)

    if t[1] == "END":
        proglen = int(LOCCTR - STARTING)
        break

    if t[0] != None:    # 有label
        if t[0] in SYMTAB:  # 有重複標籤 -> error
            print("Your assembly code has problem.")
            continue
        SYMTAB[t[0]] = LOCCTR  # 在SYMTAB放置對應LOC
    if t[1][0] == "+" and sic.find_format(t[1][1:]) == "FORMAT3or4":
        LOCCTR = LOCCTR + 4  # is format4
    elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT3or4":
        LOCCTR = LOCCTR + 3  # is format3
    elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT2":
        LOCCTR = LOCCTR + 2
    elif t[1] == "WORD":
        LOCCTR = LOCCTR + 3
    elif t[1] == "RESW":
        LOCCTR = LOCCTR + (int(t[2])*3)
    elif t[1] == "RESB":
        LOCCTR = LOCCTR + int(t[2])
    elif t[1] == "BYTE":
        if t[2][0] == 'C':
            LOCCTR = LOCCTR + (len(t[2]) - 3)
        if t[2][0] == 'X':
            # 老師這邊有寫錯，老師這邊寫'/'而不是'//'整除，LOCCTR應為整數
            LOCCTR = LOCCTR + ((len(t[2]) - 3)//2)
    elif t[1] == "BASE":
        pass


print(SYMTAB)

# PASS 2
reserveflag = False
Base_register = 0
M_record_buffer = list()

t = sicasmparser.decompositLine(lines[0])   # in order to 解決第一行的 start的設定

file = objfile.openFile(sys.argv[1])

LOCCTR = 0
if t[1] == "START":
    LOCCTR = int(t[2], 16)
    progname = t[0]

STARTING = LOCCTR  # ? STARTING 應該是存程式的開始 address (不變)

objfile.writeHeader(file, progname, STARTING, proglen)  # 存第一行

# 處理 T code
tline = ""
tstart = LOCCTR

for line in lines:
    t = sicasmparser.decompositLine(line)

    if t == (None, None, None):
        continue

    if t[1] == "START":
        continue  # START 在 pass2的頭已經處理完了

    if t[1] == "END":
        if len(tline) > 0:
            objfile.writeText(file, tstart, tline)

        # M record
        if len(M_record_buffer) > 0:
            for m_record in M_record_buffer:
                objfile.writeModification(file, m_record + 1, 20//4)

        PROGLEN = LOCCTR - STARTING

        address = STARTING
        if t[2] != None:
            address = SYMTAB[t[2]]

        objfile.writeEnd(file, address)
        break

    if t[1] in sic.OPTAB or t[1][1:] in sic.OPTAB:
        # 判斷下一個指令要加多少LOCCTR
        if t[1][0] == "+" and sic.find_format(t[1][1:]) == "FORMAT3or4":
            addition = 4  # is format4
        elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT3or4":
            addition = 3  # is format3
        elif t[1][0] != "+" and sic.find_format(t[1]) == "FORMAT2":
            addition = 2  # is format2
        # ---
        instruction = generateInstruction(t[1], t[2], SYMTAB)

        if len(instruction) == 0:
            print("Undefined Symbole: %s" % t[2])
            break

        if (LOCCTR + addition - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = instruction
        else:
            tline += instruction

        reserveflag = False

        LOCCTR += addition

    elif t[1] == "WORD":

        constant = objfile.hexstrToWord(hex(int(t[2])))

        if (LOCCTR + 3 - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = constant
        else:
            tline += constant

        reserveflag = False

        LOCCTR += 3

    elif t[1] == "BYTE":

        if t[2][0] == 'X':
            operandlen = int((len(t[2]) - 3)/2)
            constant = t[2][2:len(t[2])-1]
        elif t[2][0] == 'C':
            operandlen = int(len(t[2]) - 3)
            constant = processBYTEC(t[2])

        if (LOCCTR + addition - tstart > 30) or (reserveflag == True):
            objfile.writeText(file, tstart, tline)
            tstart = LOCCTR
            tline = constant
        else:
            tline += constant

        reserveflag = False

        LOCCTR += operandlen

    elif t[1] == "RESB":
        LOCCTR += int(t[2])
        reserveflag = True
    elif t[1] == "RESW":
        LOCCTR += (int(t[2]) * 3)
        reserveflag = True
    elif t[1] == "BASE":
        pass
    else:
        print(t[1])
        print("Invalid Instruction / Invalid Directive")
