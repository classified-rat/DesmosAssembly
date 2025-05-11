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
| 0      | 2      | Ld rx \[number\]           | ld num \-\> rx                                      |
| 1      | 2      | Ld ry \[number\]           | Ld num \-\> ry                                      |
| 2      | 1      | Mov rx acc                 | rx \+ ry \-\> acc                                   |
| 3      | 1      | add                        | Ld acc \-\> rx                                      |
| 4      | 2      | Jnz \[pointer\]            | J if top of stack is not zero, then pops            |
| 5      | 1      | Push rx                    | Push rx to stack                                    |
| 6      | 1      | Push ry                    | Push ry to stack                                    |
| 7      | 1      | Pop rx                     | Pop to rx                                           |
| 8      | 1      | Pop ry                     | Pop to ry                                           |
| 9      | 1      | Dec rx                     | Decrement rx by 1                                   |
| 10     | 1      | Dec ry                     | Decrement ry by 1                                   |
| 11     | 2      | Mov rx \[\[number\]\]      | Move number from stack to rx (negative indexed)     |
| 12     | 2      | Mov ry \[\[number\]\]      | Move number from stack to ry (negative indexed)     |
| 13     | 2      | Call \[pointer\]           | Puts a frame to stack and jumps to pointer          |
| 14     | 1      | Ret                        | Returns to normal code execution                    |
| 15     | 3      | Jl \[number\], \[pointer\] | Jump if top of stack is less than number            |
| 16     | 1      | mult                       | Rx \* ry \-\> acc                                   |
| 17     | 1      | neg                        | Rx \-\> \- rx                                       |
| 18     | 1      | inv                        | Rx \-\> 1/rx                                        |
| 19     | 1      | pop                        | Pops and discards value                             |
| 20     | 2      | Mov rx ^\[number\]         | Gets value in code from pointer                     |
| 21     | 1      | Mov rx ^ry                 | Gets a value from code at a pointer specified by ry |
| 22     | 1      | Ppsh rx                    | “Poly push” pushes value to polygon buffer          |
| 23     | 1      | poly                       | Pushes polygon to polygon stack                     |
| 24     | 1      | polypop                    | Pops a polygon from the stack                       |
| 25     | 1      | mov ^ry rx                 | Write value from rx to code at pointer from ry      |


there are 2 pseudo instructions. the first is `db` that just puts numbers in the compiled code
```
db 1,2,3,4,5 ; puts 1,2,3,4,5 in to the compiled output
-> \left[...,1,2,3,4,5,...\right] 
```

the other one is `resb`. it fills a specified amount of space with 0
```
resb 3 ; reserve 3 addresses
-> \left[...,0,0,0,...\right]
```


## Call frame

the call frame has a pointer followed by a null zero.
When the program return it **DOES NOT** pop the zero off the stack.