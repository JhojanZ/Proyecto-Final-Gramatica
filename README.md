# Compilador para Lenguaje de Alto Nivel a LLVM IR

Este proyecto tiene como objetivo desarrollar un lenguaje de alto nivel y su compilador, que traduce el código fuente al lenguaje LLVM. Luego se ejecuta el programa traducido utilizando la herramienta Clang.

## Integrantes
- **Bryan Steven Muñoz Guevara**
- **Jhojan Felipe Sánchez Zapata**

---

## Requisitos Previos

Antes de iniciar, asegúrate de tener instalados los siguientes paquetes y herramientas:

### Instalación de Librerías en Python
```bash
pip install lark
pip install pydot
pip install dot
``` 
## Descarga de Herramientas

- Graphviz  
- LLVM (Clang incluido)

## Cómo Ejecutar el Proyecto

1. Asegúrate de tener todo instalado según la sección anterior.  
2. Ejecuta los siguientes comandos en tu terminal/powershell:

### Paso 1: Compilar el código fuente
```bash
python.exe .\main.py .\input\program.src
``` 
### Paso 2: Generar y ejecutar el ejecutable
``` bash
clang .\output\program.ll -o .\program.exe
.\program.exe
``` 
### Paso 3: Verifica el código de salida
``` bash
echo $LastExitCode
``` 
# Tutorial en Video

Enlace al video explicativo (el video se encuentra cargando)
