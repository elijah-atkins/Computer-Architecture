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
        self.branchtable = {}
        #ALU ops
        self.branchtable[ADD] = self.add
        self.branchtable[SUB] = self.sub
        self.branchtable[MUL] = self.mul
        self.branchtable[DIV] = self.div
        self.branchtable[MOD] = self.mod
        self.branchtable[INC] = self.inc
        self.branchtable[DEC] = self.dec
        self.branchtable[CMP] = self.handle_cmp 
        self.branchtable[AND] = self.handle_and
        self.branchtable[NOT] = self.handle_not
        self.branchtable[OR] = self.handle_or
        self.branchtable[XOR] = self.handle_xor
        self.branchtable[SHL] = self.shl
        self.branchtable[SHR] = self.shr
        #PC mutators
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret 


        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne
        self.branchtable[JGT] = self.jgt
        self.branchtable[JLT] = self.jlt
        self.branchtable[JGE] = self.jge
        self.branchtable[JLE] = self.jle

        #Other

        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi

        self.branchtable[LD] = self.ld
        self.branchtable[ST] = self.st

        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop 
        self.branchtable[PRN] = self.prn
        self.branchtable[PRA] = self.pra
        self.ram = [0] * 256 # 256 bytes of memory
        self.register = [0] * 8 # General Purpose Registers R0 - R6
        self.register[7] = 0xF4 # R7 set to '0xF4' == '0b11110100' == '244'
        self.pc = 0 # Program Counter
        self.fl = 0 #`FL` bits: `00000LGE`
        self.sp = 7 #stack pointer to R7
        self.running = True
    # TODO implament branchtable https://en.wikipedia.org/wiki/Branch_table
    # access the RAM inside the CPU object
    # MAR (Memory Address Register) - contains the address that is 
        # being read / written to
    def ram_read(self, MAR):
        # accepts the address to read and return the value stored there
        return self.ram[MAR]
    
    # access the RAM inside the CPU object
    # MDR (Memory Data Register) - contains the data that was read or 
        # the data to write
    def ram_write(self, MDR, MAR):
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
                    if code_value == '': #handle empty lines
                        continue
                    try:
                        code_value = int(code_value, 2)
                    except ValueError:
                        print(f"Invalid Number: {code_value}")
                        sys.exit(1)

                    self.ram_write(code_value, address)
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
            self.register[reg_a] /= self.register[reg_b]
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
                self.fl = 1 #001
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 2 #010
            elif self.register[reg_a] < self.register[reg_b]:
                self.fl = 4 #100
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X  | %02X %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie, <--what's this
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2),
            self.ram_read(self.pc + 3),
            self.ram_read(self.pc + 4),

        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()
    # Branch Table Commands
    def ldi(self):
        # gets the address for registry
        operand_a = self.ram_read(self.pc + 1)
        # gets the value for the registry
        operand_b = self.ram_read(self.pc + 2)
        # Assign value to Reg Key
        self.register[operand_a] = operand_b
        # Update PC
        self.advance_pc()

    def prn(self):
        # get the address we want to print
        operand_a = self.ram[self.pc + 1]
        # Print Reg
        print(self.register[operand_a])
        # Update PC
        self.advance_pc()

    def pra(self):
        # get the address we want to print
        register_a = self.ram_read(self.pc + 1)
        # Print character

        print(chr(self.register[register_a]))
        # Update PC
        self.advance_pc()

    def hlt(self):
        # Exit Loop
        self.running = False
        # Update PC
        self.advance_pc()


    def ld(self):
        # get the address we want to print
        register_a = self.ram_read(self.pc + 1)
        register_b = self.ram_read(self.pc + 2)
        # Print character

        self.register[register_a] = self.ram[self.register[register_b]]
        # Update PC
        self.advance_pc()


    def st(self):
        # get the address we want to print
        register_a = self.ram_read(self.pc + 1)
        register_b = self.ram_read(self.pc + 2)
        # Print character
        self.register[register_b] = self.ram[self.register[register_a]]

        # Update PC
        self.advance_pc()

    def push(self):
        given_register = self.ram[self.pc + 1]
        value_in_register = self.register[given_register]
        # Decrement the stack pointer
        self.register[self.sp] -= 1
        # Write the value of the given register to memory at SP location
        self.ram[self.register[self.sp]] = value_in_register
        self.advance_pc()

    def pop(self):
        given_register = self.ram[self.pc + 1]
        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram[self.register[self.sp]]
        self.register[given_register] = value_from_memory
        # increment the stack pointer
        self.register[self.sp] += 1
        self.advance_pc()

    def call(self):
        return_address = self.pc + 2
        self.register[6] -= 1
        self.ram[self.register[6]] = return_address
        self.pc = self.register[self.ram_read(self.pc + 1)]

    def jmp(self):
        self.pc = self.register[self.ram_read(self.pc + 1)]

    def jeq(self):
        if self.fl == 1: #001
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()

    def jne(self):
        if self.fl != 1:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()
    def jgt(self):
        if self.fl == 2:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()
    def jlt(self):
        if self.fl == 4:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()
    def jge(self):
        if self.fl != 4:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()
    def jle(self):
        if self.fl != 2:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()

    def ret(self):
        SP = self.ram[self.register[6]]
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
        INSTRUCTIONS = self.ram_read(self.pc)
        number_of_times_to_increment_pc = ((INSTRUCTIONS >> 6) & 0b11) +1
        self.pc += number_of_times_to_increment_pc

    def alu_helper(self, op):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2) 
        self.alu(op, operand_a, operand_b)   
        self.advance_pc()


    def run(self):
        """Run the CPU."""
        while self.running:
            # read the memory address (MAR) that's stored in register PC (self.pc)
            # store the result in IR (Instruction Register)
            IR = self.pc
            instruction_to_execute = self.ram[IR]

            try:
                self.branchtable[instruction_to_execute]()
            
            except KeyError:
                print(f"KeyError at {self.register[self.ram[instruction_to_execute]]}")
                sys.exit(1)

