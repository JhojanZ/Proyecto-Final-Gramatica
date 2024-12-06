import sys
import os
from lark import Lark, tree
from gramatica.gramatica import gramatica
from traductor.traductor import Traductor

def main():
    if len(sys.argv) != 2:
        print(r'''
              // Wrong number of parameters!\\
              \\ python cmplc.py program.src//
              -------------------------------------
              \   ^__^ 
              \  (oo)\_______
                 (__)\       )\/\\
                     ||----w |
                     ||     ||
            ''')
        return

    input_file = sys.argv[1]
    output_file = "output/program.ll"

    with open(input_file, 'r') as inputFile:
        input = inputFile.read()

    parser = Lark(gramatica, start='inicio', keep_all_tokens=True)
    ast = parser.parse(input)

    if not os.path.exists('output'):
        os.makedirs('output')

    # Imprime el arbol
    # print(ast.pretty())
    tree.pydot__tree_to_png(ast, "output/tree.png")
    tree.pydot__tree_to_dot(ast, "output/tree.dot", rankdir="LR")

    translator = Traductor()
    with open(output_file, 'w') as out:
        translator.traducir_codigo(ast, out)
    
    print(f"Generado codigo LLVM en el archivo {output_file}")

    

if __name__ == "__main__":
    main()
