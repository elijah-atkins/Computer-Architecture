"""CPU functionality."""

import sys

# Program Actions using hex for easy ref in trace
LDI = 0x82 # 130 LOAD IMMEDIATE
PRN = 0x47 # 71 PRINT
HLT = 0x01 # 1 HALT
MUL = 0xA2 # 162 MULTIPLY
ADD = 0xA0 # 160 ADD
AND = 0xA8 # 168 AND
CALL = 0x50 # 80 CALL
CMP = 0xA7 # 167 Compare the values in two registers.
DEC = 0x66 # 102 Decrement (subtract 1 from) the value in the given register.
DIV = 0xA3 # Divide the value in the first register by the value in the second, storing the result in registerA.
INC = 0x65 # Increment (add 1 to) the value in the given register.


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes of memory
        self.reg = [0] * 7 # General Purpose Registers R0 - R6
        self.reg.append(244) # R7 set to '0xF4'
        self.pc = 0 # Program Counter
        self.fl = 0
        self.ie = 0
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
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X %02X %02X | %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ie,
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
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        running = True

        while running:
            # read the memory address (MAR) that's stored in register PC
            # store the result in Instruction Register (IR)
            IR = self.ram_read(self.pc)

            # ram_read() - read bytes at PC + 1 and PC + 2 from RAM into variables 
            # operand_a and operand_b
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # HALT
            if IR == HLT:
                # Exit Loop
                running = False
                # Update PC
                self.pc += 1

            # PRINT
            elif IR == PRN:
                # Print Reg
                print(self.reg[operand_a])
                # Update PC
                self.pc += 2

            # LDI = LOAD IMMEDIATE
            elif IR == LDI:
                # Assign value to Reg Key
                self.reg[operand_a] = operand_b
                # Update PC
                self.pc += 3
            #MUL = Multiply
            elif IR == MUL:
                # Get product
                product_of_operand = self.reg[operand_a] * self.reg[operand_b]
                # Assign value to Reg Key
                self.reg[operand_a] = product_of_operand
                # Update PC
                self.pc += 3
