# Codificador Educativo de Instrucciones RISC-V

Herramienta que traduce una única instrucción de un subconjunto RV32I a su
codificación binaria de 32 bits y en hexadecimal, mostrando de forma visual el significado
de cada campo del formato correspondiente (R, I, S o B).

Proyecto Individual - CE-4301 Arquitectura de Computadores I (2026-IIS).
Estudiante: Michael Valverde Navarro.

## Requisitos

- Python 3 (sin dependencias externas).
- Para la validación: un toolchain RISC-V de 32 bits con `as` y `objdump`.

No se requiere instalar dependencias vía `pip`.

## Uso

Todos los comandos se ejecutan desde la carpeta raíz del proyecto.

```bash
./run.sh "<instrucción>"
```

Ejemplos:

```bash
./run.sh "add x5, x6, x7"
./run.sh "addi x10, x1, -12"
./run.sh "lw x5, 8(x6)"
./run.sh "sw x8, -4(x2)"
./run.sh "beq x1, x2, 8"
```

La salida incluye el formato identificado, la codificación en binario y
hexadecimal, un desglose visual de los campos, y una línea final
`HEX: 0x........` con la codificación en 8 dígitos hexadecimales.

Si `run.sh` no tiene permiso de ejecución:

```bash
chmod +x run.sh
```

## Instrucciones soportadas

| Formato | Instrucciones |
|---|---|
| R | add, sub, and, or |
| I (aritmético) | addi, andi |
| I (carga) | lw, lb |
| S | sw, sb |
| B | beq, bne |

Restricciones de la entrada:

- Los operandos deben venir con sus valores numéricos ya resueltos (no se
  soportan etiquetas ni saltos relativos a labels).
- Los registros deben escribirse en formato `x#` (de `x0` a `x31`); no se
  aceptan los nombres ABI (`zero`, `ra`, `sp`, `t0`, `a0`, etc.).

## Validación

El script `tests/validator.py` compara la salida de la herramienta contra
el toolchain oficial para 36 casos de prueba (positivo, negativo y valor
límite por instrucción). Se ejecuta desde la carpeta raíz del proyecto:

```bash
python3 tests/validator.py
```

Requiere el toolchain instalado. Para instalarlo en Linux o WSL2:

```bash
sudo apt update
sudo apt install gcc-riscv64-unknown-elf
```

## Estructura del proyecto

```
.
├── run.sh                        # Punto de entrada
├── src/
│   └── encoder_skeleton.py       # Codificador y desglose visual
├── tests/
│   ├── validator.py              # Script de validación contra objdump
│   └── vectores_ejemplo.txt      # Vectores de ejemplo del kit dado por el profesor
├── documentation/
│   ├── doc.md                    # Documentación técnica detallada
│   └── img/                      # Imágenes de la documentación
└── README.md
```

## Documentación

Ver `documentation/doc.md` para la arquitectura del código, las fuentes de
los campos de codificación, ejemplos de salida por formato, y la evidencia
de validación.