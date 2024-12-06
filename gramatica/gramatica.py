gramatica = r"""
inicio: funciones+

funciones: "funcion" nombre_funcion "(" argumentos ")" "{" bloque_codigo "}"

argumentos: (nombre_variable ("," nombre_variable)*)?

nombre_funcion: nombre_variable -> nombre_funcion

nombre_variable:  /[_a-zA-Z]+[_.\-a-zA-Z0-9]*/

bloque_codigo: (codigo)*

codigo: return_bloque
        | if_condicional
        | expresion ";"        // Expresión como codigo (e.g., llamadas a funciones)
        | ";"             // Para permitir líneas vacías

return_bloque: "return" expresion ";"
            | "return" llamar_funcion ";"

if_condicional: "if" "(" condicion ")" "{" bloque_codigo "}"
             | "if" "(" condicion ")" "{" bloque_codigo "}" "else" "{" bloque_codigo "}"

condicion: expresion ("==" | "!=" | "<" | ">" | "<=" | ">=") expresion


expresion: term (("+" | "-") term)*
term: factor (("*" | "/") factor)* 
factor: llamar_funcion             
      | nombre_variable           
      | NUMBER                  
      | "(" expresion ")"         

llamar_funcion: nombre_funcion "(" (expresion ("," expresion)*)? ")" 

NUMBER: /[+-]?[0-9]+/ 

%ignore " "       // Ignorar espacios simples
%ignore /\r?\n/   // Ignorar saltos de línea
%ignore /\/\/.*/  // Ignorar comentarios de línea

"""