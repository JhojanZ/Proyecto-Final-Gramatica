from lark import Tree, Token
import re

class Tools:
    def __init__(self):
        self.operadores = {
            '+': 'add',
            '-': 'sub',
            '*': 'mul',
            '/': 'sdiv',
        }
        self.comparadores = { # Solo comparadores con signo
            '<': 'icmp slt',
            '<=': 'icmp sle',
            '>': 'icmp sgt',
            '>=': 'icmp sge',
            '==': 'icmp eq',
            '!=': 'icmp ne',
        }
        self.contador_variable_temp = 0 
        self.nombre_argumentos = []

    def get_nombre_argumentos(self):
        return self.nombre_argumentos
    
    def set_nombre_argumentos(self, nombre_argumentos):
        self.nombre_argumentos = nombre_argumentos 

    def get_operator_id(self, operador):
        return self.operadores.get(operador, 'unknown')  

    def get_signos_comparacion(self, operador):
        return self.comparadores.get(operador, 'unknown')

    
    def get_variable_temporal(self, isParam=False, num=0):
        self.contador_variable_temp += 1
        return f"%{self.contador_variable_temp+num}"
    
    def upload_variable_temporal(self, num):
        self.contador_variable_temp += num

    def get_propiedades(self, node, nombre):
        hijos_coincidencias = []
        for child in node.children:
            if isinstance(child, Tree):
                if child.data == nombre:  
                    hijos_coincidencias.append(child)
            elif isinstance(child, Token):
                if child.type == nombre:  
                    hijos_coincidencias.append(child)
        
        # Facilidad para retornar un solo hijo
        if len(hijos_coincidencias) == 1:
            return hijos_coincidencias[0]
        
        return hijos_coincidencias
    

    def reset_temporales(self):
        self.contador_variable_temp = 0
        self.nombre_argumentos = []

    def isNumero(self, cadena):
        if cadena.startswith(('+', '-')):
            return cadena[1:].isdigit()
        return cadena.isdigit()
    
    def convertir_numero(self, str):
        return int(re.search(r'\d+', str).group(0)) if re.search(r'\d+', str) else 0

