#Instructions to be added: 'li' 
import re
lr = 0
ilc = 0
data_sizes = { "word" : 4,"halfword":2,"byte":1,"asciiz":1, "doubleword":8}
reg_values = {"R1": 0, "R2": 3, "R3": -2, "R4": 0, "R5": 0, "R6": 0,"R7":0,"R8":0,"R9":0,"R10":0,"R11":0,"R12":0,"R13":0,"R14":0,"R15":0,"R16":0}
reg_addresses = {"R1": "00001", "R2": "00010", "R3": "00011", "R4": "00100","R5":"00101","R6":"00110","R7":"00111","R8":"01000","R9":"01001","R10":"01010","R11":"01011","R12":"01100","R13":"01101","R14":"01110","R15":"01111","R16":"10000","R17":"10001","R18":"10010","R19":"10011","R20":"10100","R21":"10101","R22":"10110","R23":"10111","R24":"11000","R25":"11001","R26":"11010","R27":"11011","R28":"11100","R29":"11101","R30":"11110","R31":"11111"}
data_addr = {}
data_ctr=0
symbol_table = {}
symbol_ctr = 0
ins = []
ins_count = 0
instructions = {"add": {"format": "xo", "op": "011111", "xo": "100001010", "oe": "0", "rc": "0"},
                "addi": {"format": "d", "op": "001110","exc":0},
                #"addis": {"format": "d", "op": "001111","exc":0},
                "and": {"format": "x", "op": "011111", "xo": "0000011100","rc":"0"},
                "andi": {"format": "d", "op": "011100","exc":0},
                "extsw": {"format": "x", "op": "011111", "rc": "0", "xo": "1111011010"},
                "nand": {"format": "x", "op": "011111", "rc": "0", },
                "or": {"format": "x", "op": "011111", "rc": "0", "xo": "0110111100"},
                "ori": {"format": "d", "op": "011000","exc":0},
                "subf": {"format": "xo", "op": "011111", "oe": "0", "xo": "000101000", "rc": "0"},
                "xor": {"format": "x", "op": "011111", "xo": "0100111100", "rc": "0"},
                "xori": {"format": "d", "op": "011010","exc":0},
                "ld": {"format": "ds", "op": "111010", "xo": "00"},
                "lwz": {"format": "d", "op": "100000","exc":1},
                "std": {"format": "ds", "op": "111110", "xo": "00"},
                "stw": {"format": "d", "op": "100100","exc":1},
                "stwu": {"format": "d", "op": "100101","exc":1},
                "lhz": {"format": "d", "op": "101000","exc":1},
                "lha": {"format": "d", "op": "101010","exc":1},
                "sth": {"format": "d", "op": "101100","exc":1},
                "lbz": {"format": "d", "op": "100010","exc":1},
                "stb": {"format": "d", "op": "100110","exc":1},
                #Skipping SHIFT/ROTATE Statements
                "b": {"format": "I", "op": "010010", "aa": "0", "lk": "0"},  # branch to relative addressing 
                "ba": {"format": "I", "op": "010010", "aa": "1", "lk": "0"}, # branch to absolute addressing
                "bl": {"format": "I", "op": "010010", "aa": "0", "lk": "1"},  # function call - branch and link - Address is absolute
                "bclr": {"format": "I", "op": "010011", "lk": "0","aa":"1"},  #function return - ASSUMED TO HAVE FORMAT 'I' and 'aa' = 1 SINCE IT IS ABSOLUTE (Stored in LR)
                "j": {"format": "I", "op": "010010", "aa": "1", "lk": "0"},  #BRANCH WITH LABEL
                "jl" : {"format":"I","op":"010010","aa":"1","lk":"1"},   
                "beqc": {"format":"b","op":"010011","aa":"0","lk":"0","type":"eq"},  #branch on condition - relative addressing
                "beqca": {"format": "b", "op": "010011", "aa": "1", "lk": "0","type":"eq"},
                "bnec": {"format": "b", "op": "010011", "aa": "0", "lk": "0","type":"ne"},
                "bneca": {"format": "b", "op": "010011", "aa": "1", "lk": "0", "type": "ne"},
                "beq": {"format": "b", "op": "010011", "aa": "1", "lk": "0"},  #BEQ WITH LABEL
                "bne": {"format": "b", "op": "010011", "aa": "1", "lk": "0"},  #BNE WITH LABEL
                 } 
o = open("machinecode.txt", "w+")

def xo(arr):
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    o.write(instructions[arr[0]]['op'] +
            reg_addresses[reg[0]] + reg_addresses[reg[1]] + reg_addresses[reg[2]] + instructions[arr[0]]['oe'] + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')

def d(arr):
    print(arr)
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    if instructions[arr[0]]['exc'] == 0:

        num = int((reg[2]))
        #The code below deals with handling negative numbers
        #and representing them as their 2's complement
        two = 2**16
        if num >= 0:
            num = bin(num)[2:].zfill(16)
        else:
            num = two + num
            num = bin(num)[2:].zfill(16)
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + str(num) + '\n')
    elif instructions[arr[0]]['exc'] == 1:
        reg = arr[1].split(',')
        opening = reg[1].index('(')
        closing = reg[1].index(')')
        offset = reg[1][0:opening]
        offset = int(offset)
        two = 2 ** 16
        if offset >= 0:
            offset = bin(offset)[2:].zfill(16)
        else:
            offset = two + offset
            offset = bin(offset)[2:].zfill(16)
        store = reg[1][opening + 1:closing]
        if len(re.findall("R", store)) == 0:
            addr = bin(data_addr[store]['addr'])[2:].zfill(5)
            o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] +
                str(addr) + str(offset)  + '\n')
            return None
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[store] + str(offset) + '\n')
                   
def x(arr):
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    if arr[0] == 'extsw':
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + '00000' + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')
        return None
    o.write(instructions[arr[0]]['op'] +
            reg_addresses[reg[0]] + reg_addresses[reg[1]] + reg_addresses[reg[2]] + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')

def ds(arr):
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    opening = reg[1].index('(')
    closing = reg[1].index(')')
    offset = reg[1][0:opening]
    offset = int(offset)
    two = 2**14
    if offset >= 0:
        offset = bin(offset)[2:].zfill(14)
    else:
        offset = two + offset
        offset = bin(offset)[2:].zfill(14)
    store = reg[1][opening + 1:closing]
    if len(re.findall("R", store)) == 0:
        addr = bin(data_addr[store]['addr'])[2:].zfill(5)
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] +
            str(addr) + str(offset) + instructions[arr[0]]['xo'] + '\n')
        return None
    o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[store] + str(offset) + instructions[arr[0]]['xo'] + '\n')

def I(arr):
    global lr
    o = open("machinecode.txt", "a+")
    if arr[0] == 'jl' or arr[0] == 'j':
        offset = symbol_table[arr[1]]['addr']
        if arr[0] == 'jl':
            lr = ilc +1 
        offset = bin(offset)[2:].zfill(24)
        o.write(instructions[arr[0]]['op'] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')
    if arr[0] == 'b' or arr[0] == 'bl' or arr[0] == 'ba':
        if arr[0] == 'bl':   #If the instruction is a branch and link (function call), then the link register should store the current instruction location register
            lr = ilc + 1
        offset = arr[1]
        offset = int(offset)
        two = 2 ** 24
        if offset >= 0:
          offset = bin(offset)[2:].zfill(24)
        else:
          offset = two + offset
          offset = bin(offset)[2:].zfill(24)
        o.write(instructions[arr[0]]['op'] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')
    elif arr[0] == 'bclr':
        offset = lr
        if offset >= 0:
            offset = bin(offset)[2:].zfill(24)
        else:
            offset = two + offset
            offset = bin(offset)[2:].zfill(24)
        o.write(instructions[arr[0]]['op'] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')

def b(arr):
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    if arr[0] == 'beq' or arr[0] == 'bne':
        offset = symbol_table[reg[2]]['addr']
        offset = bin(offset)[2:].zfill(14)
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')
        return None
    offset = reg[2]
    offset = int(offset)
    two = 2 ** 14
    if offset >= 0:
        offset = bin(offset)[2:].zfill(14)
    else:
        offset = two + offset
        offset = bin(offset)[2:].zfill(14)
    o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')
    
    
        
            
            


#print(instructions)

def readASM(path):
    global data_ctr
    global ilc
    with open(str(path), "r") as asm:
        lineList = asm.readlines()
        datapos = lineList.index(".data\n")
        textpos = lineList.index(".text\n")
        data = lineList[datapos + 1:textpos]
        text = lineList[textpos + 1:]
        #The loop below parses the data section of the ASM
        #and stores the global variable name, datatype and size
        for line in data:
            arr = line.split(" ")
            data_addr[line[0]] = {"type": arr[1][1:], "addr": data_ctr}
            if data_addr[line[0]]['type'] == 'asciiz':  #IF the global variable being declared is a string
                data_addr[line[0]]['value'] = arr[2][1:].rstrip('"\n')  #Null-terminator not added
                data_addr[line[0]]['size'] = len(arr[2][1:].rstrip('"\n'))
            elif (',' in arr[2]):                       #IF the variable being declared is an array of byte/w/hfw
                arr[2] = arr[2].rstrip('\n')
                nums = arr[2].split(',')
                for i in nums:
                    i = int(i)
                data_addr[line[0]]['value'] = nums
                data_addr[line[0]]['size'] = len(nums)
            else:                                       # ELSE
                data_addr[line[0]]['value'] = arr[2].rstrip('\n')
                data_addr[line[0]]['size'] = 1
            data_ctr = data_ctr + data_addr[line[0]]['size']*data_sizes[data_addr[line[0]]['type']]   # Maintains the counter in the data section - Similar to the global pointer
        #The loop below parses the text section of the ASM 
        #and stores the label names and addresses in a symbol table
        for line in text:
            ilc += 1
            line = line.rstrip('\n')
            arr = line.split(' ')
            if line[-1] == ":":
                symbol_table[arr[0][:-1]] = {"addr": ilc}
        ilc = 0
        for line in text:
            ilc += 1
            '''Each line, when not a label is stripped of the newline
            character and whitespaces on the right, and then split by a whitespace
            and stored as a list 'arr', which is passed to translation functions
            depending on the format of the instruction          
            '''
            line = line.rstrip('\n')
            line  = line.lstrip(' ')
            arr = line.split(' ')
            if line[-1] != ":":     #Ensures that it is not a label
                ins.append(instructions[arr[0]]['format'])
                if instructions[arr[0]]['format'] == 'xo':
                    xo(arr)
                elif instructions[arr[0]]['format'] == 'd':
                    d(arr)
                elif instructions[arr[0]]['format'] == 'x':
                    x(arr)
                elif instructions[arr[0]]['format'] == 'ds':
                    ds(arr)
                elif instructions[arr[0]]['format'] == 'I':
                    I(arr)
                elif instructions[arr[0]]['format'] == 'b':
                    b(arr)
    print(lr)
    print(ins)

def exec_xo(line):
    opcode = line[22:31]
    opcode = (int(opcode, 2))
    regsrc = [key for key, value in reg_addresses.items() if value ==line[6:11]][0]
    reg1 = [key for key, value in reg_addresses.items() if value ==line[11:16]][0]
    reg2 = [key for key, value in reg_addresses.items() if value ==line[16:21]][0]
    if opcode == 266:
        reg_values[regsrc] = reg_values[reg1] + reg_values[reg2]
        print(reg_values[regsrc])
    else:
        reg_values[regsrc] = reg_values[reg2] - reg_values[reg1]
        print(reg_values[regsrc])
    print(opcode)
        
def exec_x(line):
    opcode = line[21:31]
    opcode = (int(opcode, 2))
    regsrc = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
    reg1 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
    if opcode == 986:
        num1 = reg_values[reg1]
        if num1 >= 0:
            num1 = bin(num1)[2:].zfill(32)
        else:
            two = 2 ** 32
            num1 = two + num1
            num1 = bin(num1)[2:].zfill(32)
        num2 = ""
        for i in range(32):
            num2 += num1[0]
        reg_values[regsrc] = int(num1, 2)
        print(reg_values[regsrc])
        print(num2 + num1)
    else:
        reg2 = [key for key, value in reg_addresses.items() if value == line[16:21]][0]
        two = 2 ** 32
        num1 = reg_values[reg1]
        num2 = reg_values[reg2]
        #The calculations are done in decimal forms - stored in dest registers in decimal forms, but printed as 
        #binary numbers (2's complement)
        if opcode == 28:
            reg_values[regsrc] = num1 ^ num2
            print(reg_values[regsrc])
        elif opcode == 476:
            reg_values[regsrc] = ~(num1 ^ num2)
            print(reg_values[regsrc])
        elif opcode == 444:
            reg_values[regsrc] = num1 | num2
            print(reg_values[regsrc])
            
        elif opcode == 316:
            reg_values[regsrc] = num1 ^ num2
            print(reg_values[regsrc])
        
        #To convert decimal to 2's complement binary
        if reg_values[regsrc] >= 0:
            print(bin(reg_values[regsrc])[2:].zfill(32))
        else:
            binary = two + reg_values[regsrc]
            print(bin(binary)[2:].zfill(32))    

def exec_d(line):
    opcode = line[0:6]
    opcode = int(opcode,2)
    #The first 6 bits are UNIQUE enough to identify the instruction
    if opcode in (14, 28, 24, 26):
        two = 2**32
        regsrc = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
        reg1 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
        print(int(line[16:],2))
        if line[16] == '0':
            si = int(line[16:], 2)
        else:
            power = 2 ** 16
            si = (power - int(line[16:], 2)) * -1
        num1 = reg_values[reg1] 
        if opcode == 14:
            reg_values[regsrc] = num1 + si
        elif opcode == 28:
            reg_values[regsrc] = num1 & si
        elif opcode == 24:
            reg_values[regsrc] = num1 | si
        elif opcode == 26:
            reg_values[regsrc] = num1 ^ si
        
        print(reg_values[regsrc])
        if reg_values[regsrc] >= 0:
            print(bin(reg_values[regsrc])[2:].zfill(32))
        else:
            binary = two + reg_values[regsrc]
            print(bin(binary)[2:].zfill(32))
    else:
        two = 2 ** 16
        reg1 = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
        reg2 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
        if line[16] == '0':
            offset = int(line[16:], 2)
        else:
            offset = (two - int(line[16:], 2)) * (-1)
        base = reg_values[reg2]
        addr = base + offset
        for var in data_addr:
            if addr >= data_addr[var]['addr'] and addr <= data_addr[var]['addr'] + data_sizes[data_addr[var]['type']] * data_addr[var]['size']:
                var_name = var
        #print(var_name)
        # Implemented only lw/sw, lhz/sth, lbz/stb
        if opcode == 32:
            if data_addr[var_name]['size'] == 1:
                reg_values[reg1] = data_addr[var_name]['value']
            elif data_addr[var_name]['type'] == 'asciiz':
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] + data_addr[var_name]['value'][addr + 1] + data_addr[var_name]['value'][addr + 2] + data_addr[var_name]['value'][addr + 3]
            elif data_addr[var_name]['size'] > 1:
                elts = 4 // (data_sizes[data_addr[var_name]['type']])
                i = 0
                reg_values[reg1] =[]
                while i != elts:
                    reg_values[reg1].append(data_addr[var_name]['value'][addr + i])
                    i += 1
                print(reg_values[reg1])
        elif opcode == 40 or opcode == 42:
            if data_addr[var_name]['size'] == 1:
                reg_values[reg1] = data_addr[var_name]['value']
            elif data_addr[var_name]['type'] == 'asciiz':
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] + data_addr[var_name]['value'][addr +1] 
            elif data_addr[var_name]['size'] > 1:
                elts = 2 // (data_sizes[data_addr[var_name]['type']])
                i = 0
                reg_values[reg1] = []
                while i != elts:
                    reg_values[reg1].append(data_addr[var_name]['value'][addr + i])
                    i += 1
        elif opcode == 34:
            if data_addr[var_name]['size'] == 1:
                reg_values[reg1] = data_addr[var_name]['value']
            elif data_addr[var_name]['type'] == 'asciiz':
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] 
            elif data_addr[var_name]['size'] > 1:
                reg_values[reg1] = data_addr[var_name]['value'][addr]
        elif opcode in (36,37,44,38):
            data_addr[var_name]['value'] = reg_values[reg1]
            
def exec_ds(line):
    opcode = line[0:6]
    opcode = int(opcode, 2)
    two = 2 ** 14
    reg1 = [key for key, value in reg_addresses.items() if value ==
            line[6:11]][0]
    reg2 = [key for key, value in reg_addresses.items() if value ==
            line[11:16]][0]
    if line[16] == '0':
        offset = int(line[16:30], 2)
    else:
        offset = (two - int(line[16:30], 2)) * (-1)
    print(offset)
    base = reg_values[reg2]
    addr = base + offset
    for var in data_addr:
        if addr >= data_addr[var]['addr'] and addr <= data_addr[var]['addr'] + data_sizes[data_addr[var]['type']] * data_addr[var]['size']:
            var_name = var
    if opcode == 58:
        if data_addr[var_name]['size'] == 1:
            reg_values[reg1] = data_addr[var_name]['value']
        elif data_addr[var_name]['type'] == 'asciiz':
            addr = addr - data_addr[var_name]['addr']
            for i in range(8):
                reg_values[var_name] = data_addr[var_name]['value'][addr+i]
        elif data_addr[var_name]['size'] > 1:
            addr = addr - data_addr[var_name]['addr']
            elts = 8 // (data_sizes[data_addr[var_name]['type']])
            i = 0
            reg_values[reg1] = []
            while i != elts:
                reg_values[reg1].append(data_addr[var_name]['value'][addr + i])
                i += 1
            print(reg_values[reg1])
    elif opcode == 62:
        data_addr[var_name]['value'] = reg_values[reg1]








# def exec_I(line):

# def exec_b(line):
pc = 0

#The code above is the first part of the assignment, which is ESSENTIALLY CONVERTING ASM CODE TO BINARY
#The code below is the second part, which is EXECUTION OF BINARY CODE                 
#print(instructions[])
def execute(path):
    global ins_count
    global pc
    i = open(path, "r+")
    for line in i:
        pc += 1
        opcode = line[:6]
        ins_format = ins[ins_count]
        if ins_format == 'xo':
            exec_xo(line)
        elif ins_format == 'x':
            exec_x(line)
        elif ins_format == 'd':
            exec_d(line)
        elif ins_format == 'ds':
            exec_ds(line)
        # elif ins_format == 'I':
        #     exec_I(line)
        # elif ins_format == 'b':
        #     exec_b(line)

            
        




readASM("asm.txt")
execute("machinecode.txt")
# try:{
# print(instructions['addi']['rc'])
# }
# except: {
#     print('not found')
# }
# print("The symbol table is:")
# print(symbol_table)
#print(data_ctr)
print(data_addr)
# print(ilc)
