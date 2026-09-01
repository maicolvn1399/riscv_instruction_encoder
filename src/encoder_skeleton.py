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

SOPORTADAS = ["add", "sub", "and", "or", "addi", "andi",
              "lw", "lb", "sw", "sb", "beq", "bne"]

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

def parse_register(reg: str) -> int:

    if not reg:
        raise ValueError("Registro vacío")
    elif(reg[0] == "x"):
        extracted_reg = reg[1:]
        if (extracted_reg.isnumeric()):
            extracted_reg = int(extracted_reg)
        else: 
            raise ValueError(f"Registro No valido: x{extracted_reg}")
    else:
        raise ValueError(f"Registro No valido:{reg}")

    if (0 <= extracted_reg <= 31):
        return extracted_reg
    else:
        raise ValueError(f"Registro fuera de rango: x{extracted_reg}")




def parse_instruction(instruction: str):
    stripped = instruction.lower().strip()
    mnemonic,leftover = stripped.split(maxsplit=1)

    operands = []
    for operand in leftover.split(","):
        clean_op = operand.strip()
        if clean_op != '':
            operands.append(clean_op)
    
    
    print((mnemonic,operands))
    return (mnemonic,operands)

    
    



def encode_instruction(instruction: str) -> int:
    """
    Recibe una instrucción como texto, p. ej. "add x5, x6, x7", y debe
    retornar su codificación de 32 bits como entero (0 <= valor < 2**32).

    Debe soportar únicamente las instrucciones en SOPORTADAS. Los valores
    de opcode/funct3/funct7 de cada una NO se proveen aquí: deben
    investigarse en el manual oficial de la ISA RISC-V (ver referencia en
    la especificación) y documentarse en el README.
    """
    # TODO: implementar. Sugerencia: parsear el mnemónico y los operandos,
    # despachar según el formato (R/I/S/B), y ensamblar los campos con
    # operaciones de bits.
    raise NotImplementedError("encode_instruction: pendiente de implementar")


def explain_instruction(instruction: str, word: int) -> str:
    """
    Debe retornar un texto (para imprimirse en pantalla) que muestre, de
    forma visual, los 32 bits de 'word' divididos en los campos del
    formato correspondiente (R, I, S o B) — indicando el rango de bits y
    el valor de cada campo — junto con una breve explicación de cada uno.
    El formato visual (colores, tabla, arte ASCII, etc.) queda a su
    criterio, siempre que sea claro.
    """
    # TODO: implementar.
    raise NotImplementedError("explain_instruction: pendiente de implementar")


def main():
    if len(sys.argv) != 2:
        print(f'Uso: {sys.argv[0]} "<instruccion>"', file=sys.stderr)
        print(f'Ejemplo: {sys.argv[0]} "add x5, x6, x7"', file=sys.stderr)
        sys.exit(2)

    instruction = sys.argv[1]
    #word = encode_instruction(instruction) & 0xFFFFFFFF
    word = parse_instruction(instruction)
    for i in word[1]:
        parse_register(i)

    #print(explain_instruction(instruction, word))

    # No modificar el formato de la siguiente línea: la especificación la
    # requiere, literal, para permitir la validación automática.
    #print(f"HEX: 0x{word:08x}")


if __name__ == "__main__":
    main()
