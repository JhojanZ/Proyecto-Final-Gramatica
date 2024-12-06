from traductor.get import Tools
import re
from lark import Tree, Token

class Traductor:
    def __init__(self):
        self.utils = Tools()

    def traducir_codigo(self, ast, out):
        if ast.data == "inicio":
            for index, child in enumerate(ast.children):
                if child.data == "funciones":
                    self.traducir_funcion(child, out, index)

    def traducir_funcion(self, ast, out, index):
        nombre = self.utils.get_propiedades(ast, "nombre_funcion")
        nombre_funcion = nombre.children[0].children[0].value
        arguments = self.utils.get_propiedades(ast, "argumentos")
        
        self.utils.nombre_argumentos = []
        for arg in arguments.children:
            if isinstance(arg, Tree):
                self.utils.nombre_argumentos.append([arg.children[0].value, self.utils.get_variable_temporal(True)])
        
        # Por alguna razón después de los argumentos hay q dejar una instancia
        self.utils.get_variable_temporal(True) #------

        # Escribe la funcion
        out.write(f"define dso_local i32 @{nombre_funcion}(")
        for i, arg in enumerate(self.utils.nombre_argumentos):
            if i > 0:
                out.write(", ")
            out.write(f"i32 noundef {arg[1]}")
        out.write(f") #{str(index)} {{\n")

        # Reserva espacio para los argumentos
        for arg in self.utils.nombre_argumentos:
            temp = self.utils.get_variable_temporal()
            out.write(f"\t{temp} = alloca i32, align 4\n")
            out.write(f"\tstore i32 {arg[1]}, ptr {temp}, align 4\n")
            arg[1] = temp

        # Traduce el bloque de código
        bloque = self.utils.get_propiedades(ast, "bloque_codigo")
        retorn_expresion = []
        for child in bloque.children:
            if child.data == "codigo":
                retorn_expresion.append(self.traducir_cuerpo(child, out))
            elif child.data == "return_bloque":
                retorn_expresion.append(self.traducir_return(child, out))

        out.write(f"\tret i32 {retorn_expresion[0]}\n")
        out.write("}\n\n")
        self.utils.reset_temporales()

    def traducir_cuerpo(self, declaracion, out):
        if declaracion.children[0].data == "return_bloque":
            return self.traducir_return(declaracion.children[0], out)
        elif declaracion.children[0].data == "if_condicional":
            return self.traducir_if_condicional(declaracion.children[0], out)

    def traducir_return(self, return_stmt, out):
        expresion = self.utils.get_propiedades(return_stmt, "expresion")
        llamar_funcion = self.utils.get_propiedades(return_stmt, "llamar_funcion")

        if expresion is not None:
            return_bloque = self.traducir_expresion(expresion, out)
        elif llamar_funcion is not None:
            return_bloque = self.traducir_factor(llamar_funcion, out)

        expresion_transformada = []

        if isinstance(return_bloque, int) or isinstance(return_bloque, str):
            return return_bloque
        

        self.convertir_expresion([return_bloque], expresion_transformada)
        print("expresion_transformada", expresion_transformada)

        for expresion in expresion_transformada:
            if len(expresion[0]) == 3:
                # nsw = "no desbordamiento con signo"
                out.write(f"\t{expresion[1]} = {self.utils.get_operator_id(expresion[0][1])} nsw i32 {expresion[0][0]}, {expresion[0][2]}\n")
            
            

        # Obtener la última expresión transformada
        var_final = expresion_transformada[-1][1] if expresion_transformada else None
        print("var_final", var_final)

        return var_final
    
    def convertir_expresion(self, exp, expresion_traducida):
        for e in exp:
            if isinstance(e, list):
                # Llamada recursiva, pasando `expresion_traducida` como parámetro
                self.convertir_expresion(e, expresion_traducida)
                for arg in expresion_traducida:
                    if arg[0] in e:
                        e[e.index(arg[0])] = arg[1]

                expresion_traducida.append([e, self.utils.get_variable_temporal()])


    def traducir_if_condicional(self, if_condicional, out, save_var=None):
        condicion = self.utils.get_propiedades(if_condicional, "condicion")
        bloques = self.utils.get_propiedades(if_condicional, "bloque_codigo")
        if save_var is None:
            return_var = self.utils.get_variable_temporal()
        else:
            return_var = save_var

        # Reserva espacio para la variable de retorno
        if save_var is None:
            out.write(f"\t{return_var} = alloca i32, align 4\n")

        # Traduce la condición del if
        condicion_expr = self.traducir_condicionales(condicion, out)
        
        # Asigna valores temporales
        comp_var = self.utils.get_variable_temporal()
        true_label = self.utils.get_variable_temporal()
        final_value = self.utils.get_variable_temporal()
       
        false_label_placeholder = "##" + str(comp_var)

        print("save_var", save_var) 
        print("return_var", return_var)
        print("comp_var", comp_var) 
        print("true_label", true_label)
        print("final_value", final_value)
        
        print("false_label_placeholder", false_label_placeholder)

        # Genera la condicion
        out.write(
            f"\t{comp_var} = {self.utils.get_signos_comparacion(condicion_expr[1])} i32 {condicion_expr[0]}, {condicion_expr[2]}\n"
        )
        out.write(f"\tbr i1 {comp_var}, label {true_label}, label {false_label_placeholder}\n")
        
        

        # Bloque True
        out.write(f"\n{true_label[1:]}:\n")
        false_label = self.traducir_bloque(bloques[0] if isinstance(bloques, list) else bloques, out, return_var)
        num = 5
        end_value = self.utils.get_variable_temporal(num=num)
        print("false_label", false_label)

        # Bloque False
        if isinstance(bloques, list):
            end_label = end_value
            out.write(f"\tbr label {end_label}\n")

            out.write(f"\n{false_label[1:]}:\n")
            var_final = self.traducir_bloque(bloques[1], out, return_var)
            out.write(f"\tbr label {end_label}\n")

        else:
            end_label = end_value
            out.write(f"\tbr label {end_label}\n")
            var_final = final_value

        # Bloque Resultado
        if save_var is None:
            end_label = end_value
            var_final = self.utils.get_variable_temporal(num=num)
            out.write(f"\n{end_label[1:]}:\n")
            out.write(f"\t{var_final} = load i32, ptr {return_var}, align 4\n")
        else:
            print("save_var", save_var)
            out.write(f"\n{end_label[1:]}:\n")


      
        out.flush() 
        with open(out.name, "r+") as f:
            content = f.read()
            updated_content = content.replace(false_label_placeholder, false_label)
            f.seek(0)
            f.write(updated_content)
            f.truncate()

        return var_final

    def traducir_bloque(self, bloque, out, return_var):
        for declaracion in bloque.children:
            if declaracion.data == "codigo":
                if declaracion.children[0].data == "return_bloque":
                    return_value = self.traducir_return(declaracion.children[0], out)
                    out.write(f"\tstore i32 {return_value}, ptr {return_var}, align 4\n")
                    return self.utils.get_variable_temporal()
                elif declaracion.children[0].data == "if_condicional":
                    print("return_value", return_var)
                    return_value = self.traducir_if_condicional(declaracion.children[0], out, return_var)
                    return self.utils.get_variable_temporal()

    
    def traducir_expresion(self, expresion, out):
        expr_def = []
        for child in expresion.children:
            if isinstance(child, Tree):
                expr_def.append(self.traducir_terminos(child, out))

            elif isinstance(child, Token):
                expr_def.append(child.value)
            else:
                print("Tipo inesperado de expresión:", type(child))

        print("expr_def", expr_def)
        if len(expr_def) == 1:
            return expr_def[0]
        
        if self.utils.isNumero(expr_def[0]) and self.utils.isNumero(expr_def[2]):
            return eval(''.join(expr_def))

        return expr_def

    def traducir_terminos(self, term, out):
        term_def = []
        for child in term.children:
            if isinstance(child, Tree):  # Es un "factor"
                term_def.append(self.traducir_factor(child, out))
            elif isinstance(child, Token): # Es un operador de multiplicación o división
                term_def.append(child.value)
            else:
                print("Tipo inesperado de término:", type(child))

        if len(term_def) == 1:
            return term_def[0]
        
        return term_def

    def traducir_factor(self, factor, out):
        for child in factor.children:
            if isinstance(child, Tree):
                if child.data == "llamar_funcion":
                    # Manejo de llamadas a funciones
                    function_name = self.utils.get_propiedades(child, "nombre_funcion").children[0].children[0].value
                    
                    expr_children = self.utils.get_propiedades(child, "expresion")
                    return_expr = []
                    
                    if isinstance(expr_children, Tree):
                        return_expr.append(self.traducir_return(child, out))
                    else:
                        for arg in expr_children:
                            return_expr.append(self.traducir_expresion(arg, out))

                    args_string = ", ".join(f"i32 noundef {arg}" for arg in return_expr)

                    temp = self.utils.get_variable_temporal()
                    out.write(f"\t{temp} = call i32 @{function_name}({args_string})\n")

                    return temp

                elif child.data == "nombre_variable":
                    # Buscar el nombre de la variable en los argumentos
                    variable_name = child.children[0].value
                    for arg in self.utils.nombre_argumentos:
                        if arg[0] == variable_name:
                            var = arg[1]  # Apuntador actual del argumento

                            # Generar nueva variable temporal para la carga
                            temp = self.utils.get_variable_temporal()
                            out.write(f"\t{temp} = load i32, ptr {var}, align 4\n")
                            return temp

            elif isinstance(child, Token):
                if child.type == "NUMBER":
                    return child.value

        print("Factor", factor)
        raise ValueError(f"Factor no reconocido: {factor}")

    def traducir_condicionales(self, cond, out):
        def_condicion = []
        for child in cond.children:
            if isinstance(child, Tree):
                if child.data == "expresion":
                    def_condicion.append(self.traducir_expresion(child, out))
            elif isinstance(child, Token):
                def_condicion.append(child.value)
        return def_condicion