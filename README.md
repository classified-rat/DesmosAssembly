# Assembly reference

## registers

| register name | use              |
|---------------|------------------|
| rx            | general register |
| ry            | general register |
| acc           | accumulator      |

## operations

| opcode | length | Assembly notation          | use                                                 |
|:-------|:-------|:---------------------------|:----------------------------------------------------|
| 0      | 2      | ld rx \[number\]           | ld num \-\> rx                                      |
| 1      | 2      | ld ry \[number\]           | Ld num \-\> ry                                      |
| 2      | 1      | mov rx acc                 | rx \+ ry \-\> acc                                   |
| 3      | 1      | add                        | Ld acc \-\> rx                                      |
| 4      | 2      | jnz \[pointer\]            | J if top of stack is not zero, then pops            |
| 5      | 1      | push rx                    | Push rx to stack                                    |
| 6      | 1      | push ry                    | Push ry to stack                                    |
| 7      | 1      | pop rx                     | Pop to rx                                           |
| 8      | 1      | pop ry                     | Pop to ry                                           |
| 9      | 1      | dec rx                     | Decrement rx by 1                                   |
| 10     | 1      | dec ry                     | Decrement ry by 1                                   |
| 11     | 2      | mov rx \[\[number\]\]      | Move number from stack to rx (negative indexed)     |
| 12     | 2      | mov ry \[\[number\]\]      | Move number from stack to ry (negative indexed)     |
| 13     | 2      | call \[pointer\]           | Puts a frame to stack and jumps to pointer          |
| 14     | 1      | ret                        | Returns to normal code execution                    |
| 15     | 3      | jl \[number\], \[pointer\] | Jump if top of stack is less than number            |
| 16     | 1      | mult                       | Rx \* ry \-\> acc                                   |
| 17     | 1      | neg                        | Rx \-\> \- rx                                       |
| 18     | 1      | inv                        | Rx \-\> 1/rx                                        |
| 19     | 1      | pop                        | Pops and discards value                             |
| 20     | 2      | mov rx ^\[number\]         | Gets value in code from pointer                     |
| 21     | 1      | mov rx ^ry                 | Gets a value from code at a pointer specified by ry |
| 22     | 1      | ppsh rx                    | “Poly push” pushes value to polygon buffer          |
| 23     | 1      | poly                       | Pushes polygon to polygon stack                     |

## Call frame

the call frame has a pointer followed by a null zero.
When the program return it **DOES NOT** pop the zero off the stack.