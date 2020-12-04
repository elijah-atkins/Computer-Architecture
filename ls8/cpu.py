"""CPU functionality."""

import sys

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
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[HLT] = self.hlt
        self.branchtable[ADD] = self.add
        self.branchtable[SUB] = self.sub
        self.branchtable[MUL] = self.mul
        self.branchtable[DIV] = self.div
        self.ram = [0] * 256 # 256 bytes of memory
        self.register = [0] * 8 # General Purpose Registers R0 - R6
        self.register[7] = 0xF4 # R7 set to '0xF4' == '0b11110100' == '244'
        self.pc = 0 # Program Counter
        self.fl = 0
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
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X  | %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie, <--what's this
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2),
            self.ram_read(self.pc + 3),
            self.ram_read(self.pc + 4),
            self.ram_read(self.pc + 5),
            self.ram_read(self.pc + 6),
            self.ram_read(self.pc + 7),
            self.ram_read(self.pc + 8),
            self.ram_read(self.pc + 9),
            self.ram_read(self.pc + 10),
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()
    # Branch Table Commands
    def ldi(self):
        # gets the address for registry
        operand_a = self.ram[self.pc + 1]
        # gets the value for the registry
        operand_b = self.ram[self.pc + 2]
        # Assign value to Reg Key
        self.register[operand_a] = operand_b
        # Update PC
        self.pc += 3

    def prn(self):
        # get the address we want to print
        operand_a = self.ram[self.pc + 1]
        # Print Reg
        print(self.register[operand_a])
        # Update PC
        self.pc += 2

    def hlt(self):
        # Exit Loop
        self.running = False
        # Update PC
        self.pc += 1

    def mul(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2) 
        self.alu("MUL", operand_a, operand_b)   
        self.pc += 3 

    def div(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2) 
        self.alu("DIV", operand_a, operand_b)   
        self.pc += 3 

    def sub(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2) 
        self.alu("SUB", operand_a, operand_b)   
        self.pc += 3 

    def add(self):
        operand_a = self.ram_read(self.pc + 1)
        operand_b = self.ram_read(self.pc + 2) 
        self.alu("ADD", operand_a, operand_b)   
        self.pc += 3 

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
        # running = True

        # while running:
        #     # read the memory address (MAR) that's stored in register PC
        #     # store the result in Instruction Register (IR)
        #     IR = self.ram_read(self.pc)

        #     # ram_read() - read bytes at PC + 1 and PC + 2 from RAM into variables 
        #     # operand_a and operand_b
        #     operand_a = self.ram_read(self.pc + 1)
        #     operand_b = self.ram_read(self.pc + 2)

        #     # HALT
        #     if IR == HLT:
        #         # Exit Loop
        #         running = False
        #         # Update PC
        #         self.pc += 1

        #     # PRINT
        #     elif IR == PRN:
        #         # Print Reg
        #         print(self.register[operand_a])
        #         # Update PC
        #         self.pc += 2

        #     # LDI = LOAD IMMEDIATE
        #   elif IR == LDI:
        #         # Assign value to Reg Key
        #         self.register[operand_a] = operand_b
        #         # Update PC
        #         self.pc += 3
        #     #MUL = Multiply
        #     elif IR == MUL:
        #         # Get product
        #         product_of_operand = self.register[operand_a] * self.register[operand_b]
        #         # Assign value to Reg Key
        #         self.register[operand_a] = product_of_operand
        #         # Update PC
        #         self.pc += 3
