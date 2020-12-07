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

LDI R0,42 ;load value for *
LDI R1,10 ;load value for newline
PRA R0 ; print *
PRA R1 ; print newline
PRA R0 ; print *
PRA R0 ; print *
PRA R1 ; print newline
PRA R0 ; print *
PRA R0 ; print *
PRA R0 ; print *
PRA R0 ; print *
PRA R1 ; print newline
HLT
