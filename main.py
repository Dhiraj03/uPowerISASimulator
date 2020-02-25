import re
lr = 0
ilc = 0
data_sizes = { "word" : 4,"halfword":2,"byte":1,"asciiz":1}
registers = {"R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 0, "R6": 0}
reg_addresses = {"R1": "00001", "R2": "00010", "R3": "00011", "R4": "00100","R5":"00101","R6":"00110","R7":"00111","R8":"01000","R9":"01001","R10":"01010","R11":"01011","R12":"01100","R13":"01101","R14":"01110","R15":"01111","R16":"10000","R17":"10001","R18":"10010","R19":"10011","R20":"10100","R21":"10101","R22":"10110","R23":"10111","R24":"11000","R25":"11001","R26":"11010","R27":"11011","R28":"11100","R29":"11101","R30":"11110","R31":"11111"}
data_addr = {}
data_ctr=0
symbol_table = {}
symbol_ctr = 0
instructions = {"add": {"format": "xo", "op": "011111", "xo": "100001010", "oe": "0", "rc": "0"},
                "addi": {"format": "d", "op": "001110","exc":0},
                "addis": {"format": "d", "op": "001111","exc":0},
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
                data_addr[line[0]]['value'] = arr[1].rstrip('\n')
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

                    
            
        
        

readASM("asm.txt")
print(data_addr)
# print("The symbol table is:")
# print(symbol_table)
# print(data_ctr)
# print(ilc)
