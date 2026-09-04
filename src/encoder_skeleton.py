#!/usr/bin/env python3
"""
Esqueleto del Codificador Educativo de Instrucciones RISC-V.
CE4301 Arquitectura de Computadores I — Proyecto Individual — 2026-II

Este esqueleto ya implementa el contrato de línea de comandos y de salida
requerido por la especificación. Usted debe completar las dos funciones
marcadas con TODO; puede modificar el resto del archivo si lo necesita,
siempre que se preserve el contrato de invocación y la línea "HEX: 0x...".

No es obligatorio usar este esqueleto ni Python: puede implementar su
propia herramienta desde cero, en el lenguaje que prefiera, siempre que
respete el mismo contrato (ver especificación, sección "Modo de operación").
"""
import sys

INSTRUCTIONS = {
    "add": {"inst_type": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0000000},
    "sub": {"inst_type": "R", "opcode": 0b0110011, "funct3": 0b000, "funct7": 0b0100000},
    "and": {"inst_type": "R", "opcode": 0b0110011, "funct3": 0b111, "funct7": 0b0000000},
    "or":  {"inst_type": "R", "opcode": 0b0110011, "funct3": 0b110, "funct7": 0b0000000},
    "addi": {"inst_type": "I", "opcode": 0b0010011, "funct3": 0b000},
    "andi": {"inst_type": "I", "opcode": 0b0010011, "funct3": 0b111},
    "lw": {"inst_type": "IL", "opcode": 0b0000011, "funct3": 0b010},
    "lb": {"inst_type": "IL", "opcode": 0b0000011, "funct3": 0b000},
    "sw": {"inst_type": "S", "opcode": 0b0100011, "funct3": 0b010},
    "sb": {"inst_type": "S", "opcode": 0b0100011, "funct3": 0b000},
    "beq": {"inst_type": "B", "opcode": 0b1100011, "funct3": 0b000},
    "bne": {"inst_type": "B", "opcode": 0b1100011, "funct3": 0b001}
}


FIELDS = {
    "R":  [("funct7", 31, 25), ("rs2", 24, 20), ("rs1", 19, 15),
           ("funct3", 14, 12), ("rd", 11, 7), ("opcode", 6, 0)],
    "I":  [("imm[11:0]", 31, 20), ("rs1", 19, 15), ("funct3", 14, 12),
           ("rd", 11, 7), ("opcode", 6, 0)],
    "IL": [("imm[11:0]", 31, 20), ("rs1", 19, 15), ("funct3", 14, 12),
           ("rd", 11, 7), ("opcode", 6, 0)],
    "S":  [("imm[11:5]", 31, 25), ("rs2", 24, 20), ("rs1", 19, 15),
           ("funct3", 14, 12), ("imm[4:0]", 11, 7), ("opcode", 6, 0)],
    "B":  [("imm[12]", 31, 31), ("imm[10:5]", 30, 25), ("rs2", 24, 20),
           ("rs1", 19, 15), ("funct3", 14, 12), ("imm[4:1]", 11, 8),
           ("imm[11]", 7, 7), ("opcode", 6, 0)],
}

ROLES = {
    "rd":     "registro destino = el resultado se guarda en x{val}",
    "rs1":    "registro fuente 1 = x{val}",
    "rs2":    "registro fuente 2 = x{val}",
    "opcode": "tipo de instrucción = {bin} identifica el formato",
    "funct3": "selector de operación = {bin}",
    "funct7": "selector de operación = {bin}",
    "imm[11:0]": "inmediato de 12 bits = valor {sval}",
    "imm[11:5]": "bits altos del inmediato",
    "imm[4:0]":  "bits bajos del inmediato",
    "imm[12]":   "bit 12 del offset de salto",
    "imm[11]":   "bit 11 del offset de salto",
    "imm[10:5]": "bits 10-5 del offset de salto",
    "imm[4:1]":  "bits 4-1 del offset de salto",
}


def parse_register(reg: str) -> int:
    if not reg:
        raise ValueError("Registro vacío")
    elif reg[0] == "x":
        reg_num = reg[1:]
        if reg_num.isnumeric():
            reg_num = int(reg_num)
        else:
            raise ValueError(f"Registro no válido: x{reg_num}")
    else:
        raise ValueError(f"Registro no válido: {reg}")

    if 0 <= reg_num <= 31:
        return reg_num
    else:
        raise ValueError(f"Registro fuera de rango: x{reg_num}")


def parse_instruction(instruction: str):
    stripped = instruction.lower().strip()
    mnemonic, leftover = stripped.split(maxsplit=1)

    operands = []
    for operand in leftover.split(","):
        clean_op = operand.strip()
        if clean_op != '':
            operands.append(clean_op)

    return (mnemonic, operands)


def parse_imm(str_immediate: str) -> int:
    imm = int(str_immediate)
    if not (-2048 <= imm <= 2047):
        raise ValueError(f"Inmediato fuera de rango para tipo I: {imm} (debe estar entre -2048 y 2047)")
    else:
        return imm


def parse_memory(mem_offset: str) -> tuple:
    reg_starts = mem_offset.find("(") + 1
    reg_ends = mem_offset.rfind(")")

    reg = mem_offset[reg_starts:reg_ends]
    reg_num = parse_register(reg)

    offset = parse_imm(mem_offset[0:reg_starts - 1])

    return (offset, reg_num)


def parse_imm_type_b(imm: str) -> int:
    imm_b = int(imm)
    if imm_b % 2 != 0:
        raise ValueError(f"El offset de branch debe ser par: {imm_b}")
    if not (-4096 <= imm_b <= 4094):
        raise ValueError(f"Offset fuera de rango para tipo B: {imm_b} (debe estar entre -4096 y 4094)")
    return imm_b


def encode_r_type_inst(mnemonic, operands) -> int:
    regs = []
    for op in operands:
        regs.append(parse_register(op))

    opcode = INSTRUCTIONS[mnemonic]["opcode"]
    funct3 = INSTRUCTIONS[mnemonic]["funct3"]
    funct7 = INSTRUCTIONS[mnemonic]["funct7"]
    rd = regs[0]
    rs1 = regs[1]
    rs2 = regs[2]

    word = (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word


def encode_i_type_inst(mnemonic, operands) -> int:
    regs = []
    for op in operands:
        if op[0] != "x":
            regs.append(parse_imm(op))
        else:
            regs.append(parse_register(op))

    opcode = INSTRUCTIONS[mnemonic]["opcode"]
    funct3 = INSTRUCTIONS[mnemonic]["funct3"]
    rd = regs[0]
    rs1 = regs[1]
    imm = regs[2]

    word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word


def encode_il_type_inst(mnemonic, operands) -> int:
    rd = parse_register(operands[0])
    imm, rs1 = parse_memory(operands[1])
    opcode = INSTRUCTIONS[mnemonic]["opcode"]
    funct3 = INSTRUCTIONS[mnemonic]["funct3"]

    word = (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode
    return word


def encode_s_type_inst(mnemonic, operands) -> int:
    rs2 = parse_register(operands[0])
    imm, rs1 = parse_memory(operands[1])
    opcode = INSTRUCTIONS[mnemonic]["opcode"]
    funct3 = INSTRUCTIONS[mnemonic]["funct3"]

    imm = imm & 0xFFF
    imm_hi = (imm >> 5) & 0x7F
    imm_lo = imm & 0x1F

    word = (imm_hi << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (imm_lo << 7) | opcode
    return word


def encode_b_type_inst(mnemonic, operands) -> int:
    rs1 = parse_register(operands[0])
    rs2 = parse_register(operands[1])
    imm = parse_imm_type_b(operands[2])
    funct3 = INSTRUCTIONS[mnemonic]["funct3"]
    opcode = INSTRUCTIONS[mnemonic]["opcode"]

    imm = imm & 0x1FFF

    word = (((imm >> 12) & 0x1) << 31) | (((imm >> 5) & 0x3F) << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (((imm >> 1) & 0xF) << 8) | (((imm >> 11) & 0x1) << 7) | opcode
    return word


def render_horizontal(fmt, word):
    fields = FIELDS[fmt]
    CHARS_PER_BIT = 3
    MIN_WIDTH = 8

    cells_top = ""
    cells_mid = "|"
    cells_val = "|"
    cells_border = "+"

    for name, high, low in fields:
        nbits = high - low + 1
        value = (word >> low) & ((1 << nbits) - 1)
        val_str = format(value, f'0{nbits}b')

        width = max(nbits * CHARS_PER_BIT, MIN_WIDTH)
        width = max(width, len(name) + 2)
        width = max(width, len(val_str) + 2)

        bit_label = str(high) if high == low else f"{high}:{low}"

        cells_top += bit_label.center(width) + " "
        cells_mid += name.center(width) + "|"
        cells_val += val_str.center(width) + "|"
        cells_border += "-" * width + "+"

    return "\n".join([
        cells_top.rstrip(),
        cells_border,
        cells_mid,
        cells_border,
        cells_val,
        cells_border,
    ])


def to_signed(value, nbits):
    if value >= (1 << (nbits - 1)):
        return value - (1 << nbits)
    return value


def encode_instruction(instruction: str) -> int:
    mnemonic, operands = parse_instruction(instruction)
    inst_type = INSTRUCTIONS[mnemonic]["inst_type"]
    if inst_type == "R":
        return encode_r_type_inst(mnemonic, operands)
    elif inst_type == "I":
        return encode_i_type_inst(mnemonic, operands)
    elif inst_type == "IL":
        return encode_il_type_inst(mnemonic, operands)
    elif inst_type == "S":
        return encode_s_type_inst(mnemonic, operands)
    elif inst_type == "B":
        return encode_b_type_inst(mnemonic, operands)
    else:
        raise ValueError(f"Instrucción no soportada: {mnemonic}")


def explain_instruction(instruction: str, word: int) -> str:
    mnemonic, operands = parse_instruction(instruction)
    fmt = INSTRUCTIONS[mnemonic]["inst_type"]
    binary = format(word, '032b')
    hex_str = f"0x{word:08X}"

    overview = (
        f"Instrucción: {instruction}\n"
        f"Formato: {fmt}\n"
        f"Binario: {binary}\n"
        f"Hex: {hex_str}\n\n"
    )

    diagram = render_horizontal(fmt, word)

    roles_text = "\n\nExplicación de campos:\n"
    for name, high, low in FIELDS[fmt]:
        nbits = high - low + 1
        value = (word >> low) & ((1 << nbits) - 1)
        value_bin = format(value, f'0{nbits}b')
        bit_range = f"{high}:{low}"

        if name == "imm[11:0]":
            sval = to_signed(value, nbits)
        else:
            sval = value

        role = ROLES[name].format(val=value, bin=value_bin, sval=sval)
        roles_text += f"  {name:<10} (bits {bit_range:<6}) = {value:<6} -> {role}\n"

    return overview + diagram + roles_text


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    word = encode_instruction(instruction) & 0xFFFFFFFF

    print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()