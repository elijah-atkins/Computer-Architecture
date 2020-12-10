;histogram.ls8
;
;expected output:
;*
;**
;****
;********
;****************
;********************************
;****************************************************************


LDI R0,1 ;(LINE COUNT)
PUSH R0 ;(stack[0] = lineCount)
LDI R1,1 ;(number of hashes required for line)
LDI R0,0 ;(current hash count)
LDI R2,42 ;(symbol to print)
LDI R4,17 ;(load jump location)
PRA R2
INC R0
CMP R0,R1
JLT R4 ;(add another star) (JUMP TO line 9 IF NOT DONE WITH LINE)
LDI R2,13 

PRA R2
LDI R2,10 
PRA R2
LDI R3,2
MUL R1,R3
POP R0

INC R0
LDI R3,7
CMP R0,R3
PUSH R0
LDI R4,9

JLT R4

HLT

; R0 - current hash count for line
; R1 - total required hashes for line
; R2 - printable
; R3 - math operand (comparator, multiplier)
; R4 - jump location