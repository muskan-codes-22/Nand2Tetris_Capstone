(LOOP)

@KBD
D=M

@BLACK
D;JGT

@0
D=A
@color
M=D

@DRAW_SETUP
0;JMP

(BLACK)
@1
D=-A
@color
M=D

(DRAW_SETUP)

// Reset starting screen address
@17600
D=A
@addr
M=D

// Reset row counter
@20
D=A
@rows
M=D

(ROW_LOOP)

// Each row needs 3 words
@3
D=A
@cols
M=D

(WORD_LOOP)

// Get selected color
@color
D=M

// Write color to screen
@addr
A=M
M=D

// Move to next screen word
@addr
M=M+1

// Decrease column counter
@cols
M=M-1
D=M
@WORD_LOOP
D;JGT

// Skip remaining 29 words in this row
@29
D=A
@addr
M=D+M

// Move to next row
@rows
M=M-1
D=M
@ROW_LOOP
D;JGT

// Repeat keyboard checking
@LOOP
0;JMP