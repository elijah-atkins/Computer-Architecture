"""CPU functionality."""

import sys

# Program Actions
LDI = 130 # LOAD IMMEDIATE
PRN = 71 # PRINT
HLT = 1 # HALT
MUL = 162 #MULTIPLY


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256 # 256 bytes of memory
        self.reg = [0] * 7 # General Purpose Registers R0 - R6
        self.reg.append('0xF4') # R7 set to '0xF4'
        self.pc = 0 # Program Counter
        self.fl = 0
        self.ie = 0

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

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            130,0,8,71,0,1 #print8.ls8 in decimal 
            # From print8.ls8
            # 0b10000010, # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b01000111, # PRN R0
            # 0b00000000,
            # 0b00000001, # HLT
            #from mult.ls8
            # 0b10000010, # LDI R0,8
            # 0b00000000,
            # 0b00001000,
            # 0b10000010, # LDI R1,9
            # 0b00000001,
            # 0b00001001,
            # 0b10100010, # MUL R0,R1
            # 0b00000000,
            # 0b00000001,
            # 0b01000111, # PRN R0
            # 0b00000000,
            # 0b00000001, # HLT

        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


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

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
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
            # register_a and register_b
            register_a = self.ram_read(self.pc + 1)
            register_b = self.ram_read(self.pc + 2)

            # HALT
            if IR == HLT:
                # Exit Loop
                running = False
                # Update PC
                self.pc += 1

            # PRINT
            elif IR == PRN:
                # Print Reg
                print(self.reg[register_a])
                # Update PC
                self.pc += 2

            # LDI = LOAD IMMEDIATE
            elif IR == LDI:
                # Assign value to Reg Key
                self.reg[register_a] = register_b
                # Update PC
                self.pc += 3
            #MUL = Multiply
            elif IR == MUL:
                # Get product
                product_of_register = self.reg[register_a] * self.reg[register_b]
                # Assign value to Reg Key
                self.reg[register_a] = product_of_register
                # Update PC
                self.pc += 3

    # elif command_to_execute == ADD:
    #     register_a = memory[program_counter +1]
    #     register_b = memory[program_counter +2]
    #     sum_of_registers = registers[register_a] + registers[register_b]
    #     registers[register_a] = sum_of_registers
    #     program_counter += 3
