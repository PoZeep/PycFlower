import struct
import random


def tellme(data):
    for i in range(len(data)):
        if i % 16 == 0:
            print()
        print(hex(data[i]), end = ", ")


def getSize(code, i):
    return int(struct.unpack('H', bytes(code[i:i + 2]))[0])


def setSize(code, i, size):
    code[i] = struct.pack('H', size)[0]
    code[i + 1] = struct.pack('H', size)[1]

    return code


def sliceCode(code, version):
    # 记录代码段的 开头 与 长度
    code_attribute = []
    for i in range(len(code)):
        if code[i] == 0x73 :
            size = int(struct.unpack("<I", bytes(code[i + 1:i + 5]))[0])
            try:
                if version == "3":
                    num = 3 + i
                else:
                    num = 4 + i
                if code[size + num] == 0x53:
                    code_attribute.append({
                        'index': i + 5,
                        'len': size
                    })
            except:
                pass
    # 取出每个代码段    
    code_list = []
    for i in range(len(code_attribute)):
        code_list.append(code[code_attribute[i]['index']: code_attribute[i]['index'] + code_attribute[i]['len']])
        # tellme(code_list[i])
        # print()

    return code_attribute, code_list


def repairJump(code, version):
    relative_jump_list = [0x6E, 0x78, 0x5D]
    # 修复相对跳转
    # JUMP_FORWARD 0x6E
    # SETUP_LOOP 0x78
    # FOR_ITER 0x5D

    absolute_jump_list = [0x6F, 0x70, 0x71, 0x72, 0x73, 0x77]
    # 修复绝对跳转
    # JUMP_IF_FALSE_OR_POP 0x6F
    # JUMP_IF_TRUE_OR_POP 0x70
    # JUMP_ABSOLUTE 0x71
    # POP_JUMP_IF_FALSE 0x72
    # POP_JUMP_IF_TRUE 0x73
    # CONTINUE_LOOP 0x77

    if version == "3":
        # Python3
        for i in range(len(code)):
            if code[i] in relative_jump_list:
                cnt = 0
                jmp_range = code[i + 1] + i + 2
                if jmp_range > len(code):
                    continue
                # 如果混淆的偏移地址影响了原本跳转
                for j in range(i + 2, jmp_range):
                    # 是要混淆的目标且为指令为，因为python3都是两个字节一组，所以偶数位就是指令位
                    if code[j] == 0x64 and j % 2 == 0:
                        cnt += 1
                code[i + 1] += cnt * 12

            elif code[i] in absolute_jump_list:
                cnt = 0
                jmp_range = code[i + 1]
                if jmp_range > len(code):
                    continue
                # 如果混淆的偏移地址影响了原本跳转
                for j in range(jmp_range):
                    if code[j] == 0x64 and j % 2 == 0:
                        cnt += 1
                code[i + 1] += cnt * 12
    else:
        # Python2
        for i in range(len(code)):
            if code[i] in relative_jump_list:
                cnt = 0
                jmp_range = getSize(code, i + 1) + i + 3
                if jmp_range > len(code):
                    continue
                # 如果混淆的偏移地址影响了原本跳转
                for j in range(i + 3, jmp_range):
                    # 是要混淆的目标且为指令为，因为python2都是三个字节一组吗？？
                    # if code[j] == 0x64 and j % 3 == 0:
                    if code[j] == 0x64:
                        cnt += 1
                size = getSize(code, i + 1)
                size += 18 * cnt
                code = setSize(code, i + 1, size)

            elif code[i] in absolute_jump_list:
                cnt = 0
                jmp_range = code[i + 1]
                if jmp_range > len(code):
                    continue
                # 如果混淆的偏移地址影响了原本跳转
                for j in range(jmp_range):
                    if code[j] == 0x64:
                        cnt += 1
                size = getSize(code, i + 1)
                size += 18 * cnt
                code = setSize(code, i + 1, size)
        
    return code


def addFlower(code, version):
    obf_code = []

    if version == "3":
        # Python3
        for i in range(len(code)):
            obf_code.append(code[i])
            if code[i - 1] == 0x64 and (i - 1) % 2 == 0:
                obf_code.append(0x6E)
                obf_code.append(0)
                obf_code.append(0x6E)
                obf_code.append(4)
                for i in range(4):
                    obf_code.append(random.randint(0,255))
                obf_code.append(0x6E)
                obf_code.append(2)
                for i in range(2):
                    obf_code.append(random.randint(0,255))
    # JUMP_FORWARD  0       6E 0
    # JUMP_FORWARD  4       6E 4
    # 4个无意义字节          1 2 3 4   
    # JUMP_FORWARD  2       6E 2
    # 两个无意义字节         5 6   
    # org
    else:
    # Python2
        for i in range(len(code)):
            obf_code.append(code[i])
            if code[i - 2] == 0x64:
                obf_code.append(0x6E)
                obf_code.append(0)
                obf_code.append(0)
                obf_code.append(0x6E)
                obf_code.append(6)
                obf_code.append(0)
                for i in range(6):
                    obf_code.append(random.randint(0,255))
                obf_code.append(0x6E)
                obf_code.append(3)
                obf_code.append(0)
                for i in range(3):
                    obf_code.append(random.randint(0,255))
    # JUMP_FORWARD  0       6E 0 0
    # JUMP_FORWARD  4       6E 6 0
    # 6个无意义字节          1 2 3 4 5 6  
    # JUMP_FORWARD  2       6E 3 0
    # 3个无意义字节          7 8 9   
    # org

    return obf_code


def main(org_file, version):
    code_attribute, code_list = sliceCode(org_file, version)

    file = b''
    for i in range(len(code_attribute)):
        if len(code_list[i]) <= 0x99:
            # tellme(code_list[i])
            # print()
            code_list[i] = repairJump(code_list[i], version)
            code_list[i] = addFlower(code_list[i], version)
            # tellme(code_list[i])
        b_code_list = b''
        for t in code_list[i]:
            b_code_list += struct.pack('B', t)
        if i == 0:
            file += bytes(org_file[:code_attribute[i]['index'] - 4]) + struct.pack('<I', len(code_list[i])) + b_code_list
        else:
            file += bytes(org_file[code_attribute[i - 1]['index'] + code_attribute[i - 1]['len']:code_attribute[i]['index'] - 4]) + struct.pack('<I', len(code_list[i])) + b_code_list
    else:
        file += bytes(org_file[code_attribute[i]['index'] + code_attribute[i]['len']:])
    
    return file