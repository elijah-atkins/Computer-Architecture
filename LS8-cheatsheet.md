# LS-8 Cheatsheet

This document is non-authoritative. In cases where it differs from the spec, the
spec is correct.

## ALU ops
```
- [x] ADD  10100000 00000aaa 00000bbb
- [x] SUB  10100001 00000aaa 00000bbb
- [x] MUL  10100010 00000aaa 00000bbb
- [x] DIV  10100011 00000aaa 00000bbb
- [x] MOD  10100100 00000aaa 00000bbb

- [x] INC  01100101 00000rrr
- [x] DEC  01100110 00000rrr

- [x] CMP  10100111 00000aaa 00000bbb

- [x] AND  10101000 00000aaa 00000bbb
- [x] NOT  01101001 00000rrr
- [x] OR   10101010 00000aaa 00000bbb
- [x] XOR  10101011 00000aaa 00000bbb
- [x] SHL  10101100 00000aaa 00000bbb
- [x] SHR  10101101 00000aaa 00000bbb
```

## PC mutators
```
- [x] CALL 01010000 00000rrr
- [x] RET  00010001

- [ ] INT  01010010 00000rrr
- [ ] IRET 00010011

- [x] JMP  01010100 00000rrr
- [x] JEQ  01010101 00000rrr
- [x] JNE  01010110 00000rrr
- [x] JGT  01010111 00000rrr
- [x] JLT  01011000 00000rrr
- [x] JLE  01011001 00000rrr
- [x] JGE  01011010 00000rrr
```

## Other
```
- [ ] NOP  00000000

- [x] HLT  00000001 

- [x] LDI  10000010 00000rrr iiiiiiii

- [x] LD   10000011 00000aaa 00000bbb
- [x] ST   10000100 00000aaa 00000bbb

- [x] PUSH 01000101 00000rrr
- [x] POP  01000110 00000rrr

- [x] PRN  01000111 00000rrr
- [x] PRA  01001000 00000rrr
```