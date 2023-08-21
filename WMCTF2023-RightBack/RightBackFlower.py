import struct


def sliceCode(code):
    code_attribute = []
    for i in range(len(code)):
        if code[i] == 0x73 :
            size = int(struct.unpack("<I", bytes(code[i + 1:i + 5]))[0])
            try:
                num = 3 + i
                if code[size + num] == 0x53:
                    code_attribute.append({
                        'index': i + 5,
                        'len': size
                    })
            except:
                pass   
    code_list = []
    for i in range(len(code_attribute)):
        code_list.append(code[code_attribute[i]['index']: code_attribute[i]['index'] + code_attribute[i]['len']])

    return code_attribute, code_list


def repaitJump(code):
    flower_target = [0x6E, 0x0]
    relative_jump_list = [0x6E, 0x78, 0x5D]
    absolute_jump_list = [0x6F, 0x70, 0x71, 0x72, 0x73, 0x77]

    for i in range(len(code)):
        if code[i] in relative_jump_list:
            cnt = 0
            jmp_range = code[i + 1] + i + 2
            if jmp_range > len(code):
                continue
            for j in range(i + 2, jmp_range):
                if code[j] == flower_target[0] and code[j + 1] == flower_target[1] and j % 2 == 0:
                    cnt += 1
            code[i + 1] -= cnt * 12
        elif code[i] in absolute_jump_list:
                cnt = 0
                jmp_range = code[i + 1]
                if jmp_range > len(code):
                    continue
                for j in range(jmp_range):
                    if code[j] == flower_target[0] and code[j + 1] == flower_target[1] and j % 2 == 0:
                        cnt += 1
                code[i + 1] -= cnt * 12

    return code


def removeFlower(code):
    org_code = b''
    flowerTarget = [0x6E, 0x0]
    flower_index = []

    for i in range(len(code)):
        if code[i] == flowerTarget[0] and code[i + 1] == flowerTarget[1] and i % 2 == 0:
            flower_index.append(i)
    
    try:
        org_code += bytes(code[:flower_index[0]])
        for i in range(1, len(flower_index)):
            org_code += bytes(code[flower_index[i - 1] + 12:flower_index[i]])
        else:
            org_code += bytes(code[flower_index[i] + 12:])
    except:
        org_code = bytes(code)

    return org_code


def main():
    filename = "obf_RightBack.pyc"
    f = list(open(filename, "rb").read())


    code_attribute, code_list = sliceCode(f)
    file = b''
    for i in range(len(code_attribute)):
        if len(code_list[i]) <= 0x100:
            code_list[i] = repaitJump(code_list[i])
            code_list[i] = removeFlower(code_list[i])
        if i == 0:
            file += bytes(f[:code_attribute[i]['index'] - 4]) + struct.pack('<I', len(code_list[i])) + bytes(code_list[i])
        else:
            file += bytes(f[code_attribute[i - 1]['index'] + code_attribute[i - 1]['len']:code_attribute[i]['index'] - 4]) + struct.pack('<I', len(code_list[i])) + bytes(code_list[i])
    else:
        file += bytes(f[code_attribute[i]['index'] + code_attribute[i]['len']:])

    
    filename = 'rev_' + filename
    with open(filename, 'wb') as f:
        f.write(file)
    print("OK!")


if __name__ == "__main__":
    main()