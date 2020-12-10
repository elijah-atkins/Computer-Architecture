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
IV = 0xF8  # interrupt vector(s) (ram address) for I0
SS = 0xF3  # Address of start of stack (stack goes down from here)


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
        self.can_interrupt = False

        self.number_of_times_to_increment_pc = 0

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
                program = ls8.read().splitlines()
                ls8.close()
            # this will ignore lines that start with anything other than 0 or 1
            # and only load the first 8 characters of each line
            program = [line[:8]
                       for line in program if line and line[0] in ['0', '1']]

            for instruction in program:
                self.ram[address] = int(instruction, 2)
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
            # using floor division operator for int output
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

            self.ram_read(self.pc, 1),
            self.ram_read(self.pc, 2),
            self.ram_read(self.pc, 3),
            self.ram_read(self.pc, 4),
            self.ram_read(self.pc, 5),

        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()
    # Branch Table Commands

    def ldi(self, a, b):
        # gets the address for registry
        given_register = a
        # gets the value for the integer
        integer = b
        # Assign value to Reg Key
        self.register[given_register] = integer

    def prn(self, a):
        # get the address we want to print
        given_register = a
        # Print Reg at address we want to print
        print(self.register[given_register])

    def pra(self, a):
        # get the character value of the item stored in given register

        # print the letter without a new line
        item = self.register[a]
        if isinstance(item, int):
            print(item, chr(item))
        else:
            print(item, end='')


    def hlt(self):
        # Exit Loop
        self.running = False

    def ld(self, a, b):
        #Loads registerA with the value at the memory address stored in registerB.
        self.register[a] = self.ram_read(self.register[b], 0)

    def st(self, a, b):
        #Store value in registerB in the address stored in registerA.
        self.ram_write(self.register[a], self.register[b])

    def push(self, a):

        # Decrement the stack pointer
        self.register[SP] -= 1
        self.register[SP] &= 0xFF
        value_in_register = self.register[a]
        # Write the value of the given register to memory at SP location
        self.ram_write(self.register[SP], value_in_register)



    def pop(self, a):

        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram_read(self.register[SP], 0)
        self.register[a] = value_from_memory

        # increment the stack pointer
        self.register[SP] += 1
        self.register[SP] &= 0xFF

    def popReg(self):

        # write the value in memory at the top of stack to the given register
        value_from_memory = self.ram_read(self.register[SP], 0)
        # increment the stack pointer
        self.register[SP] += 1
        self.register[SP] &= 0xFF

        return value_from_memory

    def handle_int(self, a):
        # Issue the interrupt number stored in the given register.
        self.register[IS] = a

    def iret(self):
        '''
        1. Registers R6-R0 are popped off the stack in that order.
        2. The `FL` register is popped off the stack.
        3. The return address is popped off the stack and stored in `PC`.
        4. Interrupts are re-enabled
        '''

        for r in reversed(range(7)):
            self.pop(r)

        self.fl = self.popReg()
        self.pc = self.popReg()

        self.can_interrupt = True
        self.number_of_times_to_increment_pc = 0

    def call(self, a):
        # return address is address of instruction directly after Call
        return_address = self.pc + 2
        # add return address to ram at next lowest IS address
        self.register[IS] -= 1
        self.register[IS] &= 0xFF
        self.ram_write(self.register[IS], return_address)
        # The PC is set to the address stored in the given register.
        self.pc = self.register[a]
        self.number_of_times_to_increment_pc = 0

    def jmp(self, a):
        # Jump to the address stored in the given register.
        self.pc = self.register[a]
        self.number_of_times_to_increment_pc = 0

    def jeq(self, a):
        '''
        If `equal` flag is set (true), jump to the address stored in the given register.
        '''
        if self.fl == 1:  # 001 Equal flag is true
            self.pc = self.register[a]
            self.number_of_times_to_increment_pc = 0

    def jne(self, a):
        ''' 
        If `E` flag is clear (false, 0), jump to the address stored in the given
register.
        '''
        if self.fl != 1:
            self.pc = self.register[a]
            self.number_of_times_to_increment_pc = 0

    def jgt(self, a):
        '''
        If `greater-than` flag is set (true), jump to the address stored in the given
register.
        '''
        if self.fl == 2:
            self.pc = self.register[a]
            self.number_of_times_to_increment_pc = 0

    def jlt(self, a):
        '''
        If `less-than` flag is set (true), jump to the address stored in the given
register.
        '''
        if self.fl == 4:
            self.pc = self.register[a]
            self.number_of_times_to_increment_pc = 0

    def jge(self, a):
        '''
        If `greater-than` flag or `equal` flag is set (true), jump to the address stored
in the given register.
        '''
        if self.fl != 4:
            self.pc = self.register[a]

    def jle(self, a):

        # If `less-than` flag or `equal` flag is set (true), jump to the address stored in the given register.

        if self.fl != 2:
            self.pc = self.register[a]

    def ret(self):
        # Pop the value from the top of the stack and store it in the `PC`
        SP = self.ram_read(self.register[IS], 0)
        self.ram_write(self.register[IS], 0)
        self.pc = SP
        self.register[IS] += 1
        self.register[IS] &= 0xFF
        self.number_of_times_to_increment_pc = 0

    def mul(self, a, b):
        self.alu("MUL", a, b)

    def div(self, a, b):
        if b != 0:
            self.alu("DIV", a, b)
        else:
            print("Error, cannot divide by 0")
            self.hlt()

    def sub(self, a, b):
        self.alu("SUB", a, b)

    def add(self, a, b):
        self.alu("ADD", a, b)

    def mod(self, a, b):
        if b != 0:
            self.alu("MOD", a, b)
        else:
            print("Error, cannot perform mod, cannot divide by 0")

    def inc(self, a):
        b = 0
        self.alu("INC", a, b)

    def dec(self, a):
        b = 0
        self.alu("DEC", a, b)

    def handle_not(self, a, b):
        self.alu("NOT", a, b)

    def handle_or(self, a, b):
        self.alu("OR", a, b)

    def handle_xor(self, a, b):
        self.alu("XOR", a, b)

    def handle_and(self, a, b):
        self.alu("AND", a, b)

    def shl(self, a, b):
        self.alu("SHL", a, b)

    def shr(self, a, b):
        self.alu("SHR", a, b)

    def handle_cmp(self, a, b):
        self.alu("CMP", a, b)

    def run(self):
        """Run the CPU."""
        self.running = True
        last_runloop = datetime.now()
        interupt_interval = timedelta(seconds=0)

        while self.running:
            # read the memory address (MAR) that's stored in register PC (self.pc)
            # store the result in IR (Instruction Register)
            now = datetime.now()
            interupt_interval  += (now - last_runloop)
            last_runloop = now
            if interupt_interval.seconds >= 1:
                self.register[IS] |= 0x01
                self.register[IS] &= 0xFF
                interupt_interval -= timedelta(seconds=1)
                self.can_interrupt = True

            if self.can_interrupt:
                self.handle_interrupts()


            IR = self.pc
            instruction_to_execute = self.ram_read(IR, 0)
            self.number_of_times_to_increment_pc = (
                (instruction_to_execute >> 6) & 0b11) + 1
            operand_a = self.ram_read(IR, 1)
            operand_b = self.ram_read(IR, 2)

            try:
                if self.number_of_times_to_increment_pc == 2:
                    self.branchtable[instruction_to_execute](operand_a)
                elif self.number_of_times_to_increment_pc == 3:
                    self.branchtable[instruction_to_execute](operand_a, operand_b)
                else:
                    self.branchtable[instruction_to_execute]()

                self.pc += self.number_of_times_to_increment_pc

            except KeyError:
                print(
                    f"KeyError at {self.register[self.ram_read(instruction_to_execute, 0)]}")
                sys.exit(1)

    def handle_interrupts(self):
        masked_interrupts = self.register[IM] & self.register[IS]
        for i in range(8):
            mask = (1 << i)
            if masked_interrupts & mask:
                '''
                If a bit is set:

                1. Disable further interrupts.
                2. Clear the bit in the IS register.
                3. The `PC` register is pushed on the stack.
                4. The `FL` register is pushed on the stack.
                5. Registers R0-R6 are pushed on the stack in that order.
                6. The address (_vector_ in interrupt terminology) of the appropriate
                handler is looked up from the interrupt vector table.
                7. Set the PC is set to the handler address.
                '''


                masked_interrupts &= ~mask #clear mask flag
                self.register[IS] &= ~mask #clear register IS flag
                self.can_interrupt = False

                (temp0, temp1) = (self.register[0], self.register[1])
                (self.register[0], self.register[1]) = (self.pc, self.fl)
                self.push(0)
                self.push(1)
                (self.register[0], self.register[1]) = (temp0, temp1)

                for r in range(7):
                    self.push(r)

                self.pc = self.ram[IV + i]



