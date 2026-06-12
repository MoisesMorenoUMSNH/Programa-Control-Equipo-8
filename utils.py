# Utilidades de formato de texto
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES

import numpy as np

def formatear_numero(num):
    if np.iscomplex(num):
        return f"{num.real:.3g} {num.imag:+.3g}j"
    return f"{num.real:.3g}"

def obtener_superindice(numero):
    superindices = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
                    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻'}
    return "".join(superindices.get(digito, digito) for digito in str(numero))

def construir_polinomio(coeficientes):
    if not coeficientes:
        return "0"
    
    grado = len(coeficientes) - 1
    terminos = []
    
    for i, c in enumerate(coeficientes):
        if c == 0 and grado != 0: 
            continue
            
        potencia = grado - i
        c_str = f"{c:g}"
        
        # Ocultar el "1" o "-" unitario si acompaña a s
        if c == 1 and potencia != 0:
            c_str = ""
        elif c == -1 and potencia != 0:
            c_str = "-"
            
        if potencia == 0:
            terminos.append(f"{c:g}")
        elif potencia == 1:
            terminos.append(f"{c_str}s")
        else:
            super_potencia = obtener_superindice(potencia)
            terminos.append(f"{c_str}s{super_potencia}")
            
    if not terminos:
        return "0"
        
    return " + ".join(terminos).replace("+ -", "- ")