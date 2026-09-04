#!/usr/bin/env python3
"""
Script de validación del codificador RISC-V.
Compara la salida de la herramienta propia contra el toolchain oficial
(as + objdump) para los 36 casos de prueba, y genera una tabla de evidencia.

Uso: python3 tests/validar.py
"""
import os
import re
import subprocess
import sys

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(TESTS_DIR)
RUN_SH = os.path.join(ROOT_DIR, "run.sh")

TOOLCHAIN = "riscv64-unknown-elf-"
AS = TOOLCHAIN + "as"
OBJDUMP = TOOLCHAIN + "objdump"


TEST_CASES = [
    "add x5, x6, x7", "add x0, x1, x2", "add x31, x31, x31",
    "sub x1, x2, x3", "sub x0, x5, x6", "sub x31, x0, x1",
    "and x5, x6, x7", "and x0, x1, x2", "and x31, x30, x29",
    "or x5, x6, x7", "or x0, x1, x2", "or x31, x30, x29",
    "addi x10, x1, 100", "addi x10, x1, -12", "addi x1, x0, 2047",
    "andi x5, x6, 15", "andi x5, x6, -1", "andi x1, x0, -2048",
    "lw x5, 8(x6)", "lw x5, -8(x6)", "lw x10, 2047(x1)",
    "lb x1, 4(x2)", "lb x1, -4(x2)", "lb x0, -2048(x0)",
   "sw x8, 16(x2)", "sw x8, -4(x2)", "sw x0, 2047(x1)",
   "sb x1, 100(x2)", "sb x1, -100(x2)", "sb x3, -2048(x4)",
   "beq x1, x2, 8", "beq x5, x6, -4", "beq x0, x0, 0",
   "bne x1, x2, 16", "bne x5, x6, -16", "bne x1, x2, 4094",
]




def hex_from_my_tool(instruction):
    result = subprocess.run([RUN_SH, instruction], capture_output=True, text=True)
    output = result.stdout + result.stderr
    m = re.search(r"HEX:\s*0x([0-9a-fA-F]{8})", output)
    return m.group(1).lower() if m else None


def instruction_for_as(instruction):
    parts = instruction.split()
    mnem = parts[0].lower()
    if mnem in ("beq", "bne"):
        head, _, offset = instruction.rpartition(",")
        n = int(offset.strip())
        rel = f".+{n}" if n >= 0 else f".{n}"
        return f"{head}, {rel}"
    return instruction


def hex_from_objdump(instruction):
    asm = instruction_for_as(instruction)
    s_path = os.path.join(TESTS_DIR, "_tmp.s")
    o_path = os.path.join(TESTS_DIR, "_tmp.o")
    with open(s_path, "w") as f:
        f.write(asm + "\n")
    try:
        subprocess.run([AS, "-march=rv32i", "-mabi=ilp32", "-o", o_path, s_path],
                       check=True, capture_output=True, text=True)
        r = subprocess.run([OBJDUMP, "-d", "-M", "no-aliases,numeric", o_path],
                           check=True, capture_output=True, text=True)
    except FileNotFoundError:
        return "NO-TOOLCHAIN"
    except subprocess.CalledProcessError:
        return "ERROR-AS"
    finally:
        for p in (s_path, o_path):
            if os.path.exists(p):
                os.remove(p)
    m = re.search(r"^\s*0:\s*([0-9a-fA-F]{8})", r.stdout, re.MULTILINE)
    return m.group(1).lower() if m else None


def main():
    rows, ok, failed, no_ref = [], 0, 0, 0
    for inst in TEST_CASES:
        mine = hex_from_my_tool(inst)
        ref = hex_from_objdump(inst)
        if ref in ("NO-TOOLCHAIN", "ERROR-AS", None):
            status, no_ref = "SIN-REF", no_ref + 1
        elif mine == ref:
            status, ok = "OK", ok + 1
        else:
            status, failed = "FALLA", failed + 1
        mine_str = f"0x{mine}" if mine else "(sin salida)"
        ref_str = f"0x{ref}" if ref and ref not in ("NO-TOOLCHAIN", "ERROR-AS") else str(ref)
        rows.append((inst, mine_str, ref_str, status))

    print(f"{'Instrucción':<22} | {'Encoder propio':<12} | {'objdump':<12} | Estado")
    print("-" * 66)
    for inst, mine_str, ref_str, status in rows:
        print(f"{inst:<22} | {mine_str:<12} | {ref_str:<12} | {status}")
    print("-" * 66)
    print(f"Total: {len(TEST_CASES)}  |  OK: {ok}  |  FALLA: {failed}  |  SIN-REF: {no_ref}")
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()