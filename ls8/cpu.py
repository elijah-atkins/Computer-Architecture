"""CPU functionality."""

import sys
from time import time

# Program Actions using hex for easy ref in trace
##ALU ops
ADD = 0xA0 #10100000 160 ADD
SUB = 0xA1 #10100001 161 Subtract
MUL = 0xA2 #10100010 162 MULTIPLY
DIV = 0xA3 #10100011 Divide the value in the first register by the value in the second, storing the result in registerA.
MOD = 0xA4 #10100100 Divide the value in the first register by the value in the second, storing the _remainder_ of the result in registerA.
INC = 0x65 #01100101 Increment (add 1 to) the value in the given register.
DEC = 0x66 #01100110 102 Decrement (subtract 1 from) the value in the given register.

CMP = 0xA7 #10100111 167 Compare the values in two registers.
AND = 0xA8 #10101000 168 AND
NOT = 0x69 #01101001 Perform a bitwise-NOT on the value in a register, storing the result in the register.
OR = 0xAA #10101010 Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
XOR = 0xAB #10101011 Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
SHL = 0xAC #10101100 Shift the value in registerA left by the number of bits specified in registerB,filling the low bits with 0.
SHR = 0xAD #10101101 Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.

## PC mutators
RET = 0x11 #00010001 Return from subroutine.
IRET = 0x13 #00010011 Return from an interrupt handler.
CALL = 0x50 #01010000 80 CALL
INT = 0x52 #01010010 Issue the interrupt number stored in the given register.
JMP = 0x54 #01010100 Jump to the address stored in the given register.
JEQ = 0x55 #01010101 If `equal` flag is set (true), jump to the address stored in the given register.
JNE = 0x56 #01010110 If `E` flag is clear (false, 0), jump to the address stored in the given register.
JGT = 0x57 #01010111 If `greater-than` flag is set (true), jump to the address stored in the given register.
JLT = 0x58 #01011000 If `less-than` flag is set (true), jump to the address stored in the given register.
JLE = 0x59 #01011001 If `less-than` flag or `equal` flag is set (true), jump to the address stored in the given register.
JGE = 0x5A #01011010 If `greater-than` flag or `equal` flag is set (true), jump to the address stored in the given register.
## Other
NOP = 0x00 #00000000 do nothing
HLT = 0x01 #00000001 1 HALT
LDI = 0x82 #10000010 130 LOAD IMMEDIATE

LD = 0x83 #10000011 Loads registerA with the value at the memory address stored in registerB.
ST =0x84 #10000100 Store value in registerB in the address stored in registerA.

PUSH = 0x45 #01000101 Push the value in the given register on the stack.
POP = 0x46 #01000110 Pop the value at the top of the stack into the given register.

PRN = 0x47 #01000111 71 PRINT
PRA = 0x48 #01001000 Print alpha character value stored in the given register.


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
    # branchtable https://en.wikipedia.org/wiki/Branch_table
        self.branchtable = {
        #ALU ops
        ADD: self.add,
        SUB: self.sub,
        MUL: self.mul,
        DIV: self.div,
        MOD: self.mod,
        INC: self.inc,
        DEC: self.dec,
        CMP: self.handle_cmp, 
        AND: self.handle_and,
        NOT: self.handle_not,
        OR: self.handle_or,
        XOR: self.handle_xor,
        SHL: self.shl,
        SHR: self.shr,
        #PC mutators
        CALL: self.call,
        RET: self.ret ,
        
        INT: self.handle_int,
        IRET: self.iret,         

        JMP: self.jmp,
        JEQ: self.jeq,
        JNE: self.jne,
        JGT: self.jgt,
        JLT: self.jlt,
        JGE: self.jge,
        JLE: self.jle,

        #Other

        HLT: self.hlt,
        LDI: self.ldi,

        LD: self.ld,
        ST: self.st,

        PUSH: self.push,
        POP: self.pop,
        PRN: self.prn,
        PRA: self.pra,
        }
        self.ram = [0] * 256 # 256 bytes of memory
        self.register = [0] * 8 # General Purpose Registers R0 - R6
        self.register[7] = 0xF4 # R7 set to '0xF4' == '0b11110100' == '244'
        self.pc = 0 # Program Counter
        self.fl = 0 #`FL` bits: `00000LGE`
        self.sp = 7 #stack pointer to R7
        self.running = False


    # access the RAM inside the CPU object
    # MAR (Memory Address Register) - contains the address that is 
        # being read / written to
    def ram_read(self, MAR, shift):
        # accepts the address to read and return the value stored there
        return self.ram[MAR + shift]
    
    # access the RAM inside the CPU object
    # MDR (Memory Data Register) - contains the data that was read or 
        # the data to write
    def ram_write(self, MAR, MDR):
        # accepts a vale to write and the address to write it to
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) != 2:
            print("Usage: ls8.py filename")
            sys.exit(1)

        try:
            address = 0
            with open(sys.argv[1]) as ls8:
                for line in ls8:
                    split_line = line.split('#') #remove pounds from code
                    code_value = split_line[0].strip() #recover binary
                    if code_value == '': #ignore empty lines
                        continue
                    try: #get value of binary line
                        code_value = int(code_value, 2)
                    except ValueError: #return fault if item isn't binary digit
                        print(f"Invalid Number: {code_value}")
                        sys.exit(1)

                    self.ram_write(address, code_value)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "SUB":
            self.register[reg_a] -= self.register[reg_b]
        elif op == "MUL": 
            self.register[reg_a] *= self.register[reg_b]
        elif op == "DIV": 
#result is float not int in div when using '/'
            self.register[reg_a] //= self.register[reg_b]
        elif op == "MOD": 
            self.register[reg_a] %= self.register[reg_b]
        elif op == "INC": 
            self.register[reg_a] += 1
        elif op == "DEC": 
            self.register[reg_a] -= 1
        elif op == "NOT":
            self.register[reg_a] = ~self.register[reg_a]
        elif op == "OR":
            self.register[reg_a] |= self.register[reg_b]
        elif op == "XOR":
            self.register[reg_a] ^= self.register[reg_b]
        elif op == "AND":
            self.register[reg_a] &= self.register[reg_b]
        elif op == "SHL":
            self.register[reg_a] <<= self.register[reg_b]
        elif op == "SHR":
            self.register[reg_a] >>= self.register[reg_b]

        elif op == "CMP": #`FL` bits: `00000LGE`
            if self.register[reg_a] == self.register[reg_b]:
                self.fl = 1 #0b00000001 L and G set to 0 E set to 1 same as decimal 1 or hex 0x01
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 2 #0b00000010 L and E set to 0 G set to 1 same as decimal 2 or hex 0x02
            elif self.register[reg_a] < self.register[reg_b]:
                self.fl = 4 #0b00000100 G and E set to 0 L set to 1 same as decimal 4 or hex 0x04
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %08X  | %02X %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,#returning flag in binary
            #self.ie, <--what's this?
            self.ram_read(self.pc, 0),
            self.ram_read(self.pc, 1),
            self.ram_read(self.pc, 2),
            self.ram_read(self.pc, 3),
            self.ram_read(self.pc, 4),

        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()
    # Branch Table Commands
    def ldi(self):
        # gets the address for registry
        register_a = self.ram_read(self.pc, 1)
        # gets the value for the registry
        register_b = self.ram_read(self.pc, 2)
        # Assign value to Reg Key
        self.register[register_a] = register_b
        # Update PC
        self.advance_pc()

    def prn(self):
        # get the address we want to print
        given_register = self.ram_read(self.pc, 1)
        # Print Reg at address we want to print
        print(self.register[given_register])
        # Update PC
        self.advance_pc()

    def pra(self):
        #get the address of what we want to print
        given_register = self.ram_read(self.pc, 1)
        #get the object we want to print
        letter = self.register[given_register]
        #print the letter without a new line
        print(chr(letter), end='')
        #Update PC
        self.advance_pc()

    def hlt(self):
        # Exit Loop
        self.running = False
        # Update PC
        self.advance_pc()


    def ld(self):
        # get the address we want to print
        register_a = self.ram_read(self.pc, 1)
        register_b = self.ram_read(self.pc, 2)
        # Print character

        self.register[register_a] = self.ram_read(self.register[register_b],0)
        # Update PC
        self.advance_pc()


    def st(self):
        # get the address we want to print
        register_a = self.ram_read(self.pc, 1)
        register_b = self.ram_read(self.pc, 2)
        # Print character
        self.register[register_b] = self.ram_read(self.register[register_a], 0)

        # Update PC
        self.advance_pc()

    def push(self):
        given_register = self.ram_read(self.pc, 1)
        value_in_register = self.register[given_register]
        # Decrement the stack pointer
        self.register[self.sp] -= 1
        # Write the value of the given register to memory at SP location
        self.ram_write(self.register[self.sp], value_in_register)
        self.advance_pc()

    def pop(self):
        given_register = self.ram_read(self.pc, 1)
        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram_read(self.register[self.sp],0)
        self.register[given_register] = value_from_memory
        # increment the stack pointer
        self.register[self.sp] += 1
        self.advance_pc()

    def handle_int(self):
        pass

    def iret(self):
        pass

    def call(self):
        return_address = self.pc + 2
        self.register[6] -= 1
        self.ram_write(self.register[6], return_address)
        self.pc = self.register[self.ram_read(self.pc, 1)]

    def jmp(self):
        self.pc = self.register[self.ram_read(self.pc, 1)]

    def jeq(self):
        if self.fl == 1: #001 Equal flag is true
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def jne(self):
        if self.fl != 1:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()
    def jgt(self):
        if self.fl == 2:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()
    def jlt(self):
        if self.fl == 4:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()
    def jge(self):
        if self.fl != 4:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()
    def jle(self):
        if self.fl != 2:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def ret(self):
        SP = self.ram_read(self.register[6], 0)
        self.pc = SP
        self.register[6] += 1

    def mul(self):
        self.alu_helper("MUL")

    def div(self):
        self.alu_helper("DIV")

    def sub(self):
        self.alu_helper("SUB") 

    def add(self):
        self.alu_helper("ADD")

    def mod(self):
        self.alu_helper("MOD")

    def inc(self):
        self.alu_helper("INC")

    def dec(self):
        self.alu_helper("DEC")
    
    def handle_not(self):
        self.alu_helper("NOT")

    def handle_or(self):
        self.alu_helper("OR")

    def handle_xor(self):
        self.alu_helper("XOR")

    def handle_and(self):
        self.alu_helper("AND")
    
    def shl(self):
        self.alu_helper("SHL")

    def shr(self):
        self.alu_helper("SHR")
    
    def handle_cmp(self):
        self.alu_helper("CMP")
    
    #get number of times to increment pc from instruction binary
    def advance_pc(self):
        INSTRUCTIONS = self.ram_read(self.pc, 0)
        number_of_times_to_increment_pc = ((INSTRUCTIONS >> 6) & 0b11) +1
        self.pc += number_of_times_to_increment_pc

    def alu_helper(self, op):
        operand_a = self.ram_read(self.pc, 1)
        operand_b = self.ram_read(self.pc, 2) 
        self.alu(op, operand_a, operand_b)   
        self.advance_pc()


    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            # read the memory address (MAR) that's stored in register PC (self.pc)
            # store the result in IR (Instruction Register)
            IR = self.pc
            instruction_to_execute = self.ram_read(IR, 0)

            try:
                self.branchtable[instruction_to_execute]()
            
            except KeyError:
                print(f"KeyError at {self.register[self.ram_read(instruction_to_execute, 0)]}")
                sys.exit(1)

