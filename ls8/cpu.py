"""CPU functionality."""

import sys
from datetime import datetime, timedelta

# Program Actions using hex for easy ref in trace
# ALU ops
ADD = 0xA0  # 10100000 160 ADD
SUB = 0xA1  # 10100001 161 Subtract
MUL = 0xA2  # 10100010 162 MULTIPLY
# 10100011 Divide the value in the first register by the value in the second, storing the result in registerA.
DIV = 0xA3
# 10100100 Divide the value in the first register by the value in the second, storing the _remainder_ of the result in registerA.
MOD = 0xA4
INC = 0x65  # 01100101 Increment (add 1 to) the value in the given register.
# 01100110 102 Decrement (subtract 1 from) the value in the given register.
DEC = 0x66

CMP = 0xA7  # 10100111 167 Compare the values in two registers.
AND = 0xA8  # 10101000 168 AND
# 01101001 Perform a bitwise-NOT on the value in a register, storing the result in the register.
NOT = 0x69
# 10101010 Perform a bitwise-OR between the values in registerA and registerB, storing the result in registerA.
OR = 0xAA
# 10101011 Perform a bitwise-XOR between the values in registerA and registerB, storing the result in registerA.
XOR = 0xAB
# 10101100 Shift the value in registerA left by the number of bits specified in registerB,filling the low bits with 0.
SHL = 0xAC
# 10101101 Shift the value in registerA right by the number of bits specified in registerB, filling the high bits with 0.
SHR = 0xAD

# PC mutators
RET = 0x11  # 00010001 Return from subroutine.
IRET = 0x13  # 00010011 Return from an interrupt handler.
CALL = 0x50  # 01010000 80 CALL
INT = 0x52  # 01010010 Issue the interrupt number stored in the given register.
JMP = 0x54  # 01010100 Jump to the address stored in the given register.
JEQ = 0x55
JNE = 0x56
JGT = 0x57
JLT = 0x58
JLE = 0x59
JGE = 0x5A
# Other
NOP = 0x00  # 00000000 do nothing
HLT = 0x01  # 00000001 1 HALT
LDI = 0x82  # 10000010 130 LOAD IMMEDIATE

# 10000011 Loads registerA with the value at the memory address stored in registerB.
LD = 0x83
# 10000100 Store value in registerB in the address stored in registerA.
ST = 0x84

PUSH = 0x45  # 01000101 Push

POP = 0x46  # 01000110 Pop
PRN = 0x47  # 01000111 71 PRINT
PRA = 0x48  # 01001000 Print alpha character

IM = 0x05  # interrupt mask
IS = 0x06  # interrupt status to R6
SP = 0x07  # stack pointer to R7
IV = 0xF8  # interrupt vector(s) (ram address)


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
    # branchtable https://en.wikipedia.org/wiki/Branch_table
        self.branchtable = {
            # ALU ops
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
            # PC mutators
            CALL: self.call,
            RET: self.ret,

            INT: self.handle_int,
            IRET: self.iret,

            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            JGT: self.jgt,
            JLT: self.jlt,
            JGE: self.jge,
            JLE: self.jle,

            # Other

            HLT: self.hlt,
            LDI: self.ldi,

            LD: self.ld,
            ST: self.st,

            PUSH: self.push,
            POP: self.pop,
            PRN: self.prn,
            PRA: self.pra,
        }
        self.ram = [0] * 256  # 256 bytes of memory
        self.register = [0] * 8  # General Purpose Registers R0 - R6
        self.register[SP] = 0xF4  # R7 set to '0xF4' == '0b11110100' == '244'
        self.pc = 0  # Program Counter
        self.fl = 0  # `FL` bits: `00000LGE`

        self.running = False
        self.can_interrupt = True
    # access the RAM inside the CPU object
    # MAR (Memory Address Register) - contains the address that is
        # being read / written to

    def ram_read(self, MAR, shift):
        # accepts the address with added shift to read and return the value stored there
        return self.ram[MAR + shift]
    # access the RAM inside the CPU object
    # MDR (Memory Data Register) - contains the data that was read or
        # the data to write

    def ram_write(self, MAR, MDR):
        # accepts a vale to write and the address to write it to
        self.ram[MAR] = MDR

    def load(self):
        """Load a program into memory."""
        # if app isn't given file to run print error message
        if len(sys.argv) != 2:
            print("Usage: ls8.py filename.ls8")
            sys.exit(1)

        # load code in ls8 file into ram
        try:
            address = 0
            with open(sys.argv[1]) as ls8:
                for line in ls8:
                    split_line = line.split('#')  # remove pounds from code
                    code_value = split_line[0].strip()  # recover binary
                    if code_value == '':  # ignore empty lines
                        continue
                    try:  # get value of binary line
                        code_value = int(code_value, 2)
                    except ValueError:  # return fault if item isn't binary digit
                        print(f"Invalid Number: {code_value}")
                        sys.exit(1)

                    self.ram_write(address, code_value)
                    address += 1

        except FileNotFoundError:
            print(f"{sys.argv[1]} file not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
# adding alu from ADD example
        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == "SUB":
            self.register[reg_a] -= self.register[reg_b]
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        elif op == "DIV":
            # result is float not int in div when using '/'
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

# Compare the values in two registers.

        elif op == "CMP":  # `FL` bits: `00000LGE`
            # If they are equal, set the Equal `E` flag to 1, otherwise set it to 0.
            if self.register[reg_a] == self.register[reg_b]:
                self.fl = 1  # 0b00000001 L and G set to 0 E set to 1 same as decimal 1 or hex 0x01
# If registerA is greater than registerB, set the Greater-than `G` flag to 1, otherwise set it to 0.
            elif self.register[reg_a] > self.register[reg_b]:
                self.fl = 2  # 0b00000010 L and E set to 0 G set to 1 same as decimal 2 or hex 0x02
# If registerA is less than registerB, set the Less-than `L` flag to 1, otherwise set it to 0.
            elif self.register[reg_a] < self.register[reg_b]:
                self.fl = 4  # 0b00000100 G and E set to 0 L set to 1 same as decimal 4 or hex 0x04
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
            # self.ie, <--what's this?
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
        given_register = self.ram_read(self.pc, 1)
        # gets the value for the integer
        integer = self.ram_read(self.pc, 2)
        # Assign value to Reg Key
        self.register[given_register] = integer
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
        # get the address of what we want to print
        given_register = self.ram_read(self.pc, 1)
        # get the character value of the item stored in given register
        character_value = self.register[given_register]
        # print the letter without a new line
        print(chr(character_value), end='')
        # Update PC
        self.advance_pc()

    def hlt(self):
        # Exit Loop
        self.running = False
        # Update PC
        self.advance_pc()

    def ld(self):
        # Loads register_a with the value at the
        # memory address stored in register_b.
        register_a = self.ram_read(self.pc, 1)
        register_b = self.ram_read(self.pc, 2)

        self.register[register_a] = self.ram_read(self.register[register_b], 0)
        # Update PC
        self.advance_pc()

    def st(self):
        # Loads register_b with the value at the
        # memory address stored in register_a.
        register_a = self.ram_read(self.pc, 1)
        register_b = self.ram_read(self.pc, 2)

        self.register[register_b] = self.ram_read(self.register[register_a], 0)

        # Update PC
        self.advance_pc()

    def push(self):
        given_register = self.ram_read(self.pc, 1)
        value_in_register = self.register[given_register]
        # Decrement the stack pointer
        self.register[SP] -= 1
        # Write the value of the given register to memory at SP location
        self.ram_write(self.register[SP], value_in_register)
        self.advance_pc()

    def pop(self):
        given_register = self.ram_read(self.pc, 1)
        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram_read(self.register[SP], 0)
        self.register[given_register] = value_from_memory
        # increment the stack pointer
        self.register[SP] += 1
        self.advance_pc()

    def handle_int(self):
        # Issue the interrupt number stored in the given register.
        given_register = self.ram_read(self.pc, 1)
        self.register[IS] = given_register

    def iret(self):
        '''
        1. Registers R6-R0 are popped off the stack in that order.
        2. The `FL` register is popped off the stack.
        3. The return address is popped off the stack and stored in `PC`.
        4. Interrupts are re-enabled
        '''
        pass
        # self.trace()
        # for r in range(6, -1, -1):
        #     self.register.pop(r)
        # (temp0, temp1) = (self.register[0], self.register[1])
        # (self.fl, self.pc) = (self.reg[0], self.reg[1])
        # (self.reg[0], self.reg[1]) = (temp0, temp1)
        # self.can_interrupt = True

    def call(self):
        # return address is address of instruction directly after Call
        return_address = self.pc + 2
        # add return address to ram at next lowest IS address
        self.register[IS] -= 1
        self.ram_write(self.register[IS], return_address)
        # The PC is set to the address stored in the given register.
        self.pc = self.register[self.ram_read(self.pc, 1)]

    def jmp(self):
        # Jump to the address stored in the given register.
        self.pc = self.register[self.ram_read(self.pc, 1)]

    def jeq(self):
        '''
        If `equal` flag is set (true), jump to the address stored in the given register.
        '''
        if self.fl == 1:  # 001 Equal flag is true
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def jne(self):
        ''' 
        If `E` flag is clear (false, 0), jump to the address stored in the given
register.
        '''
        if self.fl != 1:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def jgt(self):
        '''
        If `greater-than` flag is set (true), jump to the address stored in the given
register.
        '''
        if self.fl == 2:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def jlt(self):
        '''
        If `less-than` flag is set (true), jump to the address stored in the given
register.
        '''
        if self.fl == 4:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def jge(self):
        '''
        If `greater-than` flag or `equal` flag is set (true), jump to the address stored
in the given register.
        '''
        if self.fl != 4:
            self.pc = self.register[self.ram_read(self.pc + 1)]
        else:
            self.advance_pc()

    def jle(self):

        # If `less-than` flag or `equal` flag is set (true), jump to the address stored in the given register.

        if self.fl != 2:
            self.pc = self.register[self.ram_read(self.pc, 1)]
        else:
            self.advance_pc()

    def ret(self):
        # Pop the value from the top of the stack and store it in the `PC`
        SP = self.ram_read(self.register[IS], 0)
        self.ram_write(self.register[IS], 0)
        self.pc = SP
        self.register[IS] += 1

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

    # get number of times to increment pc from instruction binary
    def advance_pc(self):
        INSTRUCTIONS = self.ram_read(self.pc, 0)
        number_of_times_to_increment_pc = ((INSTRUCTIONS >> 6) & 0b11) + 1
        self.pc += number_of_times_to_increment_pc

    def alu_helper(self, op):
        # get register a and register b and run through alu
        register_a = self.ram_read(self.pc, 1)
        register_b = self.ram_read(self.pc, 2)
        self.alu(op, register_a, register_b)
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
                print(
                    f"KeyError at {self.register[self.ram_read(instruction_to_execute, 0)]}")
                sys.exit(1)
