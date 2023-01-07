from sklearn.datasets import make_sparse_coded_signal


def getMainFileName(filename):
    i = 0
    mainname = ""
    while True:
        if filename[i] == '.':
            break
        mainname += filename[i]
        i += 1
    return mainname


def openFile(filename):
    objfilename = getMainFileName(filename)
    objfilename = objfilename + ".obj"
    objfile = open(objfilename, "w")
    return objfile


def writeHeader(file, name, starting, proglen):
    header = "H" + programname(name)
    header += hexstrToWord(hex(starting))
    header += hexstrToWord(hex(proglen))
    header += "\n"
    file.write(header)


def programname(name):
    n = 6 - len(name)
    for i in range(0, n):
        name = name + ' '
    return name


def writeText(file, starting, tline):
    textrecord = "T" + hexstrToWord(hex(starting))
    l = hex(int(len(tline)/2))
    l = l[2:]  # 把0x去掉

    n = 2 - len(l)
    for i in range(0, n):
        l = '0' + l

    l = l.upper()
    textrecord += l
    textrecord += tline
    textrecord += "\n"
    file.write(textrecord)


def writeEnd(file, address):
    endrecord = "E" + hexstrToWord(hex(address))
    file.write(endrecord)
    file.close()


def writeModification(file, starting_address_field, address_field_len):
    M_record = "M" + hexstrToWord(hex(starting_address_field))
    M_record += hexstrToWord(hex(address_field_len))[-2:]
    M_record += "\n"
    file.write(M_record)


def hexstrToWord(hexstr):
    hexstr = hexstr.upper()
    hexstr = hexstr[2:]
    n = 6 - len(hexstr)
    for i in range(0, n):
        hexstr = '0' + hexstr
    return hexstr
