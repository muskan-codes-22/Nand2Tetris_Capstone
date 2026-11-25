
import sys
import re
from pathlib import Path


# Predefined symbols
symbols = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "SCREEN": 16384,
    "KBD": 24576
}

# R0 to R15
for i in range(16):
    symbols[f"R{i}"] = i


# Hack comp table
comp_table = {
    "0":   "0101010",
    "1":   "0111111",
    "-1":  "0111010",
    "D":   "0001100",
    "A":   "0110000",
    "!D":  "0001101",
    "!A":  "0110001",
    "-D":  "0001111",
    "-A":  "0110011",
    "D+1": "0011111",
    "A+1": "0110111",
    "D-1": "0001110",
    "A-1": "0110010",
    "D+A": "0000010",
    "D-A": "0010011",
    "A-D": "0000111",
    "D&A": "0000000",
    "D|A": "0010101",

    "M":   "1110000",
    "!M":  "1110001",
    "-M":  "1110011",
    "M+1": "1110111",
    "M-1": "1110010",
    "D+M": "1000010",
    "D-M": "1010011",
    "M-D": "1000111",
    "D&M": "1000000",
    "D|M": "1010101"
}

# Hack dest table
dest_table = {
    "":    "000",
    "M":   "001",
    "D":   "010",
    "MD":  "011",
    "A":   "100",
    "AM":  "101",
    "AD":  "110",
    "AMD": "111"
}

# Hack jump table
jump_table = {
    "":    "000",
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}


# Read and clean the assembly file
def clean_file(filename):
    instructions = []

    with open(filename, "r") as file:
        for line in file:
            line = line.split("//")[0].strip()
            line = "".join(line.split())

            if line:
                instructions.append(line)

    return instructions


# Pass 1: Find labels
def first_pass(instructions):
    rom_address = 0

    for line in instructions:
        if line.startswith("(") and line.endswith(")"):
            label = line[1:-1]

            if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", label):
                raise ValueError(f"Invalid label: {label}")

            if label in symbols:
                print(f"Warning: Duplicate label '{label}'")
            else:
                symbols[label] = rom_address

        else:
            rom_address += 1


# Convert C-instruction
def convert_c(line):
    dest = ""
    jump = ""

    if "=" in line:
        parts = line.split("=")

        if len(parts) != 2:
            raise ValueError("Invalid C-instruction")

        dest, line = parts

    if ";" in line:
        parts = line.split(";")

        if len(parts) != 2:
            raise ValueError("Invalid C-instruction")

        line, jump = parts

    if line not in comp_table:
        raise ValueError(f"Invalid computation: {line}")

    if dest not in dest_table:
        raise ValueError(f"Invalid destination: {dest}")

    if jump not in jump_table:
        raise ValueError(f"Invalid jump: {jump}")

    return "111" + comp_table[line] + dest_table[dest] + jump_table[jump]


# Pass 2: Generate machine code
def second_pass(instructions):
    machine_code = []
    next_variable = 16

    for line in instructions:

        # Ignore labels
        if line.startswith("(") and line.endswith(")"):
            continue

        # A-instruction
        if line.startswith("@"):
            symbol = line[1:]

            if symbol.isdigit():
                address = int(symbol)

                if address > 32767:
                    raise ValueError("Address out of range")

            else:
                if not re.fullmatch(r"[A-Za-z_.$:][A-Za-z0-9_.$:]*", symbol):
                    raise ValueError(f"Invalid symbol: {symbol}")

                if symbol not in symbols:
                    symbols[symbol] = next_variable
                    next_variable += 1

                address = symbols[symbol]

            binary = format(address, "016b")

        # C-instruction
        else:
            binary = convert_c(line)

        machine_code.append(binary)

    return machine_code


# Main assembler function
def assemble(filename):
    instructions = clean_file(filename)

    first_pass(instructions)
    machine_code = second_pass(instructions)

    output_file = Path(filename).with_suffix(".hack")

    with open(output_file, "w") as file:
        for instruction in machine_code:
            file.write(instruction + "\n")

    print("Assembly completed successfully!")
    print(f"Output file: {output_file}")


# Run the assembler
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py filename.asm")
    else:
        try:
            assemble(sys.argv[1])
        except (ValueError, OSError) as error:
            print("Error:", error)
