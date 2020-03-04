#Instructions to be added: 'li' 
import re    #Imports the regular expression library 

lr = 0       #Stores the address that the control should return to - LINK REGISTER
ilc = 0      #Instruction location counter - Stores the offset of each instruction (Relative addressing of each instruction)

#data_sizes is a dict that stores the size of each datatype in the data section
data_sizes = {"word": 4, "halfword": 2, "byte": 1, "asciiz": 1, "doubleword": 8}

#reg_values is a dict that stores the contents of the CPU registers(32)
reg_values = {"R1": 0, "R2": 0, "R3": 0, "R4": 0, "R5": 1, "R6": 0,"R7":0,"R8":0,"R9":0,"R10":0,"R11":0,"R12":0,"R13":0,"R14":0,"R15":0,"R16":0}

#reg_addresses is a dict that stores the 5-bit address of each of the 32 registers
reg_addresses = {"R1": "00001", "R2": "00010", "R3": "00011", "R4": "00100","R5":"00101","R6":"00110","R7":"00111","R8":"01000","R9":"01001","R10":"01010","R11":"01011","R12":"01100","R13":"01101","R14":"01110","R15":"01111","R16":"10000","R17":"10001","R18":"10010","R19":"10011","R20":"10100","R21":"10101","R22":"10110","R23":"10111","R24":"11000","R25":"11001","R26":"11010","R27":"11011","R28":"11100","R29":"11101","R30":"11110","R31":"11111"}


#data_addr is a dict that contains the details of all GLOBAL VARIABLES DECLARED AND INITIALISED in the data section of the asm
#file, stored along with
# 1. Type - datatype
# 2. Value - value that the variable is initialised with
# 3. Size - number of data items in the global variable
# 4. Address - Starting address of the global variable
data_addr = {}

#data_ctr stores the offset of the position of each global variable in the data section
data_ctr = 0

#symbol_table is a dict that stores the names(labels) and relative addresses of all labels in the text section 
symbol_table = {}
symbol_ctr = 0

#ins is a list that stores the formats of all the instructions present in the text section of the asm file
ins = []
#ins_count stores the number of instructions present in the text section
ins_count = 0


#instructions is a dict that contains all the valid instructions, along with their 
# 1. Format - x,xo,d,b,ds,etc
# 2. Opcode(not unique) - 6-digit opcode
# 3. Format-specific fields for each instruction

#Skipping SHIFT/ROTATE Statements
instructions = {"add": {"format": "xo", "op": "011111", "xo": "100001010", "oe": "0", "rc": "0"},
                "addi": {"format": "d", "op": "001110","exc":0},
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
                #aa = 1 means that ABSOLUTE ADDRESSING is used
                #aa = 0 means that RELATIVE ADDRESSING is used
                "b": {"format": "I", "op": "010010", "aa": "0", "lk": "0"},  # branch to relative addressing 
                "ba": {"format": "I", "op": "010010", "aa": "1", "lk": "0"}, # branch to absolute addressing
                "bl": {"format": "I", "op": "010010", "aa": "0", "lk": "1"}, # function call - branch and link - Address is absolute
                "bclr": {"format": "I", "op": "010011", "aa":"1","lk":"0"}, #function return - ASSUMED TO HAVE FORMAT 'I' and 'aa' = 1 SINCE IT IS ABSOLUTE (Stored in LR)
                "j": {"format": "I", "op": "010100", "aa": "1", "lk": "0"},  #BRANCH WITH LABEL
                "jl" : {"format":"I","op":"010100","aa":"1","lk":"1"},       #BRANCH WITH LABEL and link
                "beqc": {"format":"b","op":"010000","aa":"0","lk":"0"},  #branch on condition - relative addressing
                "beqca": {"format": "b", "op": "010000", "aa": "1", "lk": "0"}, #branch on condition - absolute addressing
                "bnec": {"format": "b", "op": "010001", "aa": "0", "lk": "0"},  #BNE - relative addressing
                "bneca": {"format": "b", "op": "010001", "aa": "1", "lk": "0"}, #BNE - absolute addressing
                "beq": {"format": "b", "op": "010010", "aa": "1", "lk": "0"},  #BEQ WITH LABEL
                "bne": {"format": "b", "op": "010011", "aa": "1", "lk": "0"},  #BNE WITH LABEL
                 } 
#the file 'machinecode.txt' contains the source assembly code
o = open("machinecode.txt", "w+")

#The functions below are used to handle the conversion of asm code to binary format
# Each function is specific to an instruction format
def xo(arr):
    '''
    Straightforward code, bundles the opcode, register codes and other fields and prints it in binary format in the output file
    '''
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    o.write(instructions[arr[0]]['op'] +
            reg_addresses[reg[0]] + reg_addresses[reg[1]] + reg_addresses[reg[2]] + instructions[arr[0]]['oe'] + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')

def d(arr):
    '''
    The set of instructions with format 'd' are of two kinds - addi R1,R2,5 (OR) lwz R1,0(R2)
    One where the signed immediate field is present before the register(enclosed in brackets) (exc : 1)
    and the other where it is clearly separated from the registers by commas (exc : 0)
    '''
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    
    #The below if-else checks whether exc = 1 or 0 
    if instructions[arr[0]]['exc'] == 0:
        #The signed-immediate field is separated from the registers by commas
        #num is the SI field
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
        #The SI field is present outside the paranthesized registers
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
        #** what does this do
        if len(re.findall("R", store)) == 0:
            addr = bin(data_addr[store]['addr'])[2:].zfill(5)
            o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] +
                str(addr) + str(offset)  + '\n')
            return None
        #**
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[store] + str(offset) + '\n')
                   
def x(arr):
    '''
    Except the 'extsw' instruction, every other instruction contains 3
    3 registers in the instruction
    '''
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    if arr[0] == 'extsw':
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + '00000' + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')
        return None
    o.write(instructions[arr[0]]['op'] +
            reg_addresses[reg[0]] + reg_addresses[reg[1]] + reg_addresses[reg[2]] + instructions[arr[0]]['xo'] + instructions[arr[0]]['rc'] + '\n')

def ds(arr):
    '''
    This instruction format is used for ld and std (Load/Store doubleword)
    '''
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
    #** wtf
    if len(re.findall("R", store)) == 0:
        addr = bin(data_addr[store]['addr'])[2:].zfill(5)
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] +
            str(addr) + str(offset) + instructions[arr[0]]['xo'] + '\n')
        return None
    #**
    o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[store] + str(offset) + instructions[arr[0]]['xo'] + '\n')

def I(arr):
    '''
    The branching, jumping and linking statement use I-format
    It contains different number and type of arguments depending on the instruction
    '''
    global lr
    o = open("machinecode.txt", "a+")
    
    if arr[0] == 'jl' or arr[0] == 'j':
        #The jump and jump and link instructions are PSEUDO-INSTRUCTIONS
        #The relative address/offset of the label (from the symbol table) is taken as the SI field
        offset = symbol_table[arr[1]]['addr']
        if arr[0] == 'jl':
            lr = ilc +1        #if the instruction is of jump AND LINK kind
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
    '''
    This is used for the BEQ/BNE sets of instructions which can be used
    with relative/absolute addresses or labels, and this function is responsible
    for handling all the different instructions
    '''
    o = open("machinecode.txt", "a+")
    reg = arr[1].split(',')
    
    #if the instruction is a LABELLED beq/bne
    if arr[0] == 'beq' or arr[0] == 'bne':
        offset = symbol_table[reg[2]]['addr']
        offset = bin(offset)[2:].zfill(14)
        o.write(instructions[arr[0]]['op'] + reg_addresses[reg[0]] + reg_addresses[reg[1]] + str(offset) + instructions[arr[0]]['aa'] + instructions[arr[0]]['lk'] + '\n')
        return None
    
    #This offset is calculated for relative/absolute addressing
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
    
    #The below code is used to read the assembly code file
    with open(str(path), "r") as asm:
        lineList = asm.readlines()              #lineList is a list of all the lines in the asm code
        #DATA SECTION SHOULD COME BEFORE THE TEXT SECTION - It is COMPULSORY to have BOTH DATA AND TEXT SECTION
        datapos = lineList.index(".data\n")  #datapos is the index of the '.data' line 
        textpos = lineList.index(".text\n")  #textpos is the index of the '.text' line
        
        #The list of lines is divided into two lists - data section and text section
        data = lineList[datapos + 1:textpos]
        text = lineList[textpos + 1:]
        
        
        #The loop below parses the data section of the asm file
        #and stores the global variable name, datatype and size
        for line in data:
            arr = line.split(" ")
            #each line is of the form
            # varname: .<datatype> <value(s)>      
            #The data_addr dict is updated with the new global variable
            data_addr[line[0]] = {"type": arr[1][1:], "addr": data_ctr}
            if data_addr[line[0]]['type'] == 'asciiz':  #IF the global variable being declared is a string
                data_addr[line[0]]['value'] = arr[2][1:].rstrip('"\n')  #Null-terminator not added
                data_addr[line[0]]['size'] = len(arr[2][1:].rstrip('"\n'))
            elif (',' in arr[2]):                       #IF the variable being declared is an array of byte/word/halfword
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
        
        #FIRST PASS OF 2-PASS ASSEMBLER
        for line in text:
            ilc += 1   #The instruction location counter is incremented by 1 each time a line is read from the text section
            line = line.rstrip('\n')
            arr = line.split(' ')
            if line[-1] == ":":   #checks whether the last character of the line is a ':' (LABEL) or not
                symbol_table[arr[0][:-1]] = {"addr": ilc - 1}
        
        #The ILC is reset to 0 to store BEFORE THE SECOND PASS OF THE ASSEMBLER
        
        #SECOND PASS OF 2-PASS ASSEMBLER
        ilc = 0
        for line in text:
            ilc += 1
            '''Each line, when not a label is stripped of the newline
            character and whitespaces on the right, and then split by a whitespace
            and stored as a list 'arr', which contains the  which is passed to translation functions
            depending on the format of the instruction  
            The line is split by whitespace to easily access the different components of a line - such as a label/instruction name/ registers/ SI field
            '''
            line = line.rstrip('\n')
            line  = line.lstrip(' ')
            arr = line.split(' ')
            
            #If the line is not a label, then it is processed by calling a translation function 
            #specific to the format of the instruction
            if line[-1] != ":":       #Ensures that it is not a label
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
    #.. anything to print for testing
'''
.............................................................................................................
                                      ASSEMBLY IS COMPLETE - NEXT STEP IS BINARY EXECUTION
.............................................................................................................
'''

#It is very IMPORTANT to identify a field/ set of fields that as a unique key/ identifier for each instruction to perform 
#instruction-specific operations - Each instruction format has a different set of unique field
pc = 0
def exec_xo(line):
    global pc
    print("The result is : ")
    #The 'xo' field of the 'xo' format is a unique way of identifying a particular instruction
    opcode = line[22:31]
    opcode = (int(opcode, 2))
    #The register arguments of the instruction are retrieved
    regsrc = [key for key, value in reg_addresses.items() if value ==line[6:11]][0]
    reg1 = [key for key, value in reg_addresses.items() if value ==line[11:16]][0]
    reg2 = [key for key, value in reg_addresses.items() if value ==line[16:21]][0]
    if opcode == 266:   #add
        reg_values[regsrc] = int(reg_values[reg1]) + int(reg_values[reg2])
        print(reg_values[regsrc])
    else:               #subf 
        reg_values[regsrc] = reg_values[reg2] - reg_values[reg1]
        print(reg_values[regsrc])
    pc += 1
    
        
def exec_x(line):
    global pc
    print("The result is :")
    #The 'xo' field of the 'x' format is a unique identifier for every instruction
    opcode = line[21:31]
    opcode = (int(opcode, 2))
    #The register arguments of the instruction are retrieved
    regsrc = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
    reg1 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
    if opcode == 986:    #extsw => the lower 32 bits of the register are the same as src register and the upper 32 bits are sign extended
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
        #If the instruction is not 'extsw', then the second source register is also retrieved
        reg2 = [key for key, value in reg_addresses.items() if value == line[16:21]][0]
        two = 2 ** 32
        num1 = reg_values[reg1]
        num2 = reg_values[reg2]
        #The calculations are done in decimal forms - stored in dest registers in decimal forms, but printed as 
        #binary numbers (2's complement)
        if opcode == 28:   #and
            reg_values[regsrc] = num1 & num2
            print(reg_values[regsrc])
        elif opcode == 476:  #nand
            reg_values[regsrc] = ~(num1 & num2)
            print(reg_values[regsrc])
        elif opcode == 444:   #or
            reg_values[regsrc] = num1 | num2
            print(reg_values[regsrc])
            
        elif opcode == 316:  #xor
            reg_values[regsrc] = num1 ^ num2
            print(reg_values[regsrc])
        
        #To convert decimal to 2's complement binary
        # if reg_values[regsrc] >= 0:
        #     print(bin(reg_values[regsrc])[2:].zfill(32))
        # else:
        #     binary = two + reg_values[regsrc]
        #     print(bin(binary)[2:].zfill(32))
    pc += 1

def exec_d(line):
    global pc
    print("The value stored/loaded is : ")
    #The 'po' field of the 'd' instruction format is the unique identifier for each instruction
    opcode = line[0:6]
    opcode = int(opcode,2)
    #The first 6 bits are UNIQUE enough to identify the instruction
    #The if-else below checks whether the instruction has exc = 1 or exc = 0
    if opcode in (14, 28, 24, 26):
        two = 2**32
        #The register arguments of the instruction are retrieved
        regsrc = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
        reg1 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
        if line[16] == '0':
            si = int(line[16:], 2)
        else:
            power = 2 ** 16
            si = (power - int(line[16:], 2)) * -1
        num1 = reg_values[reg1] 
        if opcode == 14:    #addi
            reg_values[regsrc] = num1 + si
        elif opcode == 28:  #andi
            reg_values[regsrc] = num1 & si
        elif opcode == 24:  #ori
            reg_values[regsrc] = num1 | si
        elif opcode == 26:  #xori
            reg_values[regsrc] = num1 ^ si
        print(reg_values[regsrc])
       
        # if reg_values[regsrc] >= 0:
        #     print(bin(reg_values[regsrc])[2:].zfill(32))
        # else:
        #     binary = two + reg_values[regsrc]
        #     print(bin(binary)[2:].zfill(32))
    else:
        two = 2 ** 16
        #The register arguments of the instruction are retrieved
        reg1 = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
        reg2 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
        #The offset is the SI field in the instruction
        if line[16] == '0':
            offset = int(line[16:], 2)
        else:
            offset = (two - int(line[16:], 2)) * (-1)
        #The base address is the register address code of the src register
        base = reg_values[reg2]
        #The offset in the SI field is added to the base address to get the final src address
        addr = base + offset
        
        #The loop below is written to find the global variable that is being referred to by the address
        for var in data_addr:
            if addr >= data_addr[var]['addr'] and addr <= data_addr[var]['addr'] + data_sizes[data_addr[var]['type']] * data_addr[var]['size']:
                var_name = var
        
        # Implemented only lw/sw, lhz/sth, lbz/stb
        if opcode == 32:   #lwz
            if data_addr[var_name]['size'] == 1:   #if the data type is a word,halfword or byte
                reg_values[reg1] = int(data_addr[var_name]['value'])
            elif data_addr[var_name]['type'] == 'asciiz':  #if the data type is asciiz
                #To find the range of addresses relative to the starting address of the global variable
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] + data_addr[var_name]['value'][addr + 1] + data_addr[var_name]['value'][addr + 2] + data_addr[var_name]['value'][addr + 3]
            elif data_addr[var_name]['size'] > 1:  #if the data item is an array of word/halfword/byte
                elts = 4 // (data_sizes[data_addr[var_name]['type']])   #to find the number of elements to be retrieved
                if elts == 1:
                    reg_values[reg1] = int(data_addr[var_name]['value'][addr])
                else:
                    reg_values[reg1] =[]
                    for i in range(elts):
                        reg_values[reg1].append(data_addr[var_name]['value'][addr + i])                    
            print(reg_values[reg1])
        
        elif opcode == 40 or opcode == 42:   #lhz or lha
            if data_addr[var_name]['size'] == 1:
                reg_values[reg1] = int(data_addr[var_name]['value'])
            elif data_addr[var_name]['type'] == 'asciiz':
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] + data_addr[var_name]['value'][addr +1] 
            elif data_addr[var_name]['size'] > 1:
                elts = 2 // (data_sizes[data_addr[var_name]['type']])
                if elts == 1:
                    reg_values[reg1] = int(data_addr[var_name]['value'][addr])          
                else:
                    reg_values[reg1] = []
                    for i in range(elts):
                        reg_values[reg1].append(data_addr[var_name]['value'][addr + i])
            print(reg_values[reg1])
        
        elif opcode == 34:    #lbz
            if data_addr[var_name]['size'] == 1:
                reg_values[reg1] = int(data_addr[var_name]['value'])
            elif data_addr[var_name]['type'] == 'asciiz':
                addr = addr - data_addr[var_name]['addr']
                reg_values[reg1] = data_addr[var_name]['value'][addr] 
            elif data_addr[var_name]['size'] > 1:
                reg_values[reg1] = int(data_addr[var_name]['value'][addr])
            print(reg_values[reg1])
        elif opcode in (36,37,44,38): #lhz/lha/lb/lwz
            data_addr[var_name]['value'] = reg_values[reg1]
            print(data_addr[var_name]['value'])
    pc += 1
            
def exec_ds(line):
    global pc
    print("The value stored/loaded : ")
    #The 'po' field of the 'ds' format is the unique identifier for each instruction
    opcode = line[0:6]
    opcode = int(opcode, 2)
    
    #The given offset is found, and the register arguments are retrieved
    two = 2 ** 14
    reg1 = [key for key, value in reg_addresses.items() if value ==
            line[6:11]][0]
    reg2 = [key for key, value in reg_addresses.items() if value ==
            line[11:16]][0]
    if line[16] == '0':
        offset = int(line[16:30], 2)
    else:
        offset = (two - int(line[16:30], 2)) * (-1)
    

    base = reg_values[reg2]
    addr = base + offset
    #The final address is calculated by adding the offset to the value of the address stored in the source register
    
    #The loop below is written to find the global variable that is being referred to by the address
    for var in data_addr:
        if addr >= data_addr[var]['addr'] and addr <= data_addr[var]['addr'] + data_sizes[data_addr[var]['type']] * data_addr[var]['size']:
            var_name = var
    
    if opcode == 58:   #ld - Doubleword
        if data_addr[var_name]['size'] == 1:
            reg_values[reg1] = int(data_addr[var_name]['value'])
            print(reg_values[reg1])
        elif data_addr[var_name]['type'] == 'asciiz':
            addr = addr - data_addr[var_name]['addr']
            for i in range(8):
                reg_values[var_name] = data_addr[var_name]['value'][addr + i]
            print(reg_values[reg1])
        elif data_addr[var_name]['size'] > 1:
            addr = addr - data_addr[var_name]['addr']
            elts = 8 // (data_sizes[data_addr[var_name]['type']])
            if elts == 1:
                reg_values[reg1] = int(data_addr[var_name]['value'][addr])
            else:    
                reg_values[reg1] = []
                for i in range(elts):
                    reg_values[reg1].append(data_addr[var_name]['value'][addr + i])
            print(reg_values[reg1])
    
    elif opcode == 62: #std
        data_addr[var_name]['value'] = reg_values[reg1]
        print(data_addr[var_name]['value'])
    pc += 1



def exec_I(line):
    '''
    The program counter (PC) and Link register (LR) are accessed and updated in this function
    as it takes care of the unconditional jump instructions
    '''
    global pc
    global lr
    print("Jumping to instruction number : ")
    
    opcode = int(line[0:6],2)
    two = 2**24
    if line[6] == '0':
        offset = int(line[6:30], 2)
    else:
        offset = (two + int(line[6:30], 2)) * (-1)
        
    aa = int(line[30],2)
    lk = int(line[31],2)
    #The 'po', 'aa' and 'lk' fields are used together to uniquely identify a specific instruction
    if opcode == 18 and aa == 0 and lk == 0:   #b - unconditional jump with relative addressing
        pc += offset
    elif opcode == 18 and aa == 1 and lk == 0:  #ba - unconditional jump with absolute addressing
        pc = offset
    elif opcode == 18 and aa == 0 and lk == 1:  #bl - unconditional branch and LINK with relative addressing
        lr = pc + 1
        pc += offset   
    elif opcode == 19 and aa == 1 and lk == 0:  #bclr - function return statement
        pc = lr
    elif opcode == 20 and aa == 1 and lk == 0:  #j - unconditional jump WITH LABEL
        pc = int(line[6:30], 2)
    elif opcode == 20 and aa == 1 and lk == 1: #jl - unconditional jump and link with LABEL
        lr = pc + 1
        pc = int(line[6:30], 2)
    print(pc)
    

def exec_b(line):
    global pc
    global lr
    print("Jumping to instruction number : ")
    '''
    Handles the execution of the set of branch-one-equal and branch-when-not-equal instructions 
    '''
    opcode = int(line[0:6], 2)
    aa = int(line[30])
    two = 2**14
    if line[16] == '0':
        offset = int(line[16:30], 2)
    else:
        offset = (two + int(line[16:30], 2)) * (-1)
    
    #The values stored in the two source registers are retrieved TO COMPARE
    reg1 = [key for key, value in reg_addresses.items() if value == line[6:11]][0]
    reg2 = [key for key, value in reg_addresses.items() if value == line[11:16]][0]
    num1 = reg_values[reg1]
    num2 = reg_values[reg2]
    

    if opcode == 16 and aa == 0:   #beqc - BRANCH ON EQUAL - RELATIVE
        if num1 == num2:
            pc += offset
        else:
            pc += 1
    elif opcode == 16 and aa == 1:  #beqca - BRANCH ON EQUAL - ABSOLUTE
        if num1 == num2:
            pc = offset
        else:
            pc += 1
    elif opcode == 17 and aa == 0:  #bnec - BRANCH WHEN NOT EQUAL - RELATIVE
        if num1 != num2:
            pc += offset
        else:
            pc += 1
    elif opcode == 17 and aa == 1:  #bneca - BRANCH WHEN NOT EQUAL - ABSOLUTE
        if num1 != num2:
            pc = offset
        else:
            pc += 1
    elif opcode == 18 and aa == 1:  #beq - BRANCH ON EQUAL - LABEL
        if num1 == num2:
            pc = offset
        else:
            pc += 1
    elif opcode == 19 and aa == 1: #bne - BRANCH WHEN NOT EQUAL - LABEL
        if num1 != num2:
            pc = offset
        else:
            pc += 1
    print(pc)


#The code below is the second part, which is EXECUTION OF BINARY CODE                 
def execute(path,ins_count):
    '''
    this function is used to execute a SPECIFIC LINE of the binary file - Path is the argument that specifies
    the relative/absolute path of the file that contains assembled binary code and ins is the line number / 
    instruction offset of the instruction to be executed
    '''
    global pc
    global lr
    print("Currently executing instruction : " + str(ins_count))
    lr = 1
    i = open(path, "r+")
    arr = i.readlines()
    line = arr[ins_count]          #The required line is chosen from the list of lines in the binary file with the help of ins
                             #The PC(program counter) is used to keep a track of which instruction is being executed - by default, it is incremented by 1 after every instruction
    ins_format = ins[ins_count]
    if ins_format == 'xo':
        exec_xo(line)
    elif ins_format == 'x':
        exec_x(line)
    elif ins_format == 'd':
        exec_d(line)
    elif ins_format == 'ds':
        exec_ds(line)
    elif ins_format == 'I':
        exec_I(line)
    elif ins_format == 'b':
       exec_b(line)
    #ENSURE THAT THERE IS NO JUMP/BRANCH STATEMENT IN LAST INSTRUCTION
    if (pc == len(arr) ):
        return None
    else:
        execute("machinecode.txt",pc)

            
        




readASM("asm.txt")
print("The details of all global variables declared in the data section are : ")
print(data_addr)
print("The symbol table is : ")
print(symbol_table)
execute("machinecode.txt", 0)  #The 'execute' statement is called with 0 as the ins_count



#.. printing for testing
