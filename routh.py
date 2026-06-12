# Análisis de Estabilidad del Criterio de Routh-Hurwitz
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES

import sympy as sp
from utils import obtener_superindice

def analizar_con_k(coeficientes_k):
    K_sym = sp.Symbol('K', real=True)
    n = len(coeficientes_k) - 1
    
    lineas = []
    lineas.append("=== DISEÑO DE ESTABILIDAD CON PARAMETRO K ===")
    lineas.append(f"Grado del polinomio: {n}")
    lineas.append(f"Coeficientes: {coeficientes_k}\n")

    tabla = _construir_tabla(coeficientes_k, n)
    
    # Tabla de Routh
    ancho_col = 24
    max_cols = max(len(f) for f in tabla)
    ancho_etiq = 6
    ancho_total = ancho_etiq + 3 + (ancho_col * max_cols)
    separador = "-" * ancho_total

    lineas.append(separador)
    lineas.append(" Tabla de Routh-Hurwitz (con K simbolico)".center(ancho_total))
    lineas.append(separador)
    for i, fila in enumerate(tabla):
        potencia = n - i
        celdas = [f"{sp.simplify(e)!s}".center(ancho_col) for e in fila]
        etiqueta = f"s{obtener_superindice(potencia)}"
        lineas.append(f" {etiqueta:<{ancho_etiq}}| {''.join(celdas)}")
        lineas.append(separador)
        
    # Primera columna y condiciones
    lineas.append("\nPrimera columna:")
    condiciones = []
    for i, fila in enumerate(tabla):
        elemento = sp.simplify(fila[0])
        potencia = n - i
        etiqueta = f"s{obtener_superindice(potencia)}"
        lineas.append(f"{etiqueta}: {elemento}")
        
        try:
            if K_sym not in elemento.free_symbols:
                elem_eval = elemento
                if sp.Symbol('epsilon') in elemento.free_symbols:
                    eps = sp.Symbol('epsilon', positive=True)
                    elem_eval = elemento.subs(sp.Symbol('epsilon'), eps)
                
                eval_bool = sp.simplify(elem_eval > 0)
                if eval_bool == sp.true:
                    cond = "Siempre se cumple (True)"
                elif eval_bool == sp.false:
                    cond = "Nunca se cumple (False)"
                else:
                    cond = str(eval_bool)
            else:
                cond = sp.solve(elemento > 0, K_sym)
            condiciones.append((potencia, elemento, cond))
        except Exception:
            condiciones.append((potencia, elemento, None))

    lineas.append("\nCondiciones para estabilidad (cada elemento > 0):")
    for potencia, elem, cond in condiciones:
        etiqueta = f"s{obtener_superindice(potencia)}"
        if cond is not None:
            lineas.append(f"{etiqueta}: {elem} > 0  =>  {cond}")
        else:
            lineas.append(f"{etiqueta}: {elem} > 0  (condicion no resuelta)")

    lineas.append("\n--- Rango de K para estabilidad ---")
    
    inecuaciones = []
    sistema_siempre_inestable = False
    
    for fila in tabla:
        elem = sp.simplify(fila[0])
        elem_eval = elem
        if sp.Symbol('epsilon') in elem.free_symbols:
            eps = sp.Symbol('epsilon', positive=True)
            elem_eval = elem.subs(sp.Symbol('epsilon'), eps)
            
        if K_sym in elem_eval.free_symbols:
            inecuaciones.append(elem_eval > 0)
        else:
            if sp.simplify(elem_eval > 0) == sp.false:
                sistema_siempre_inestable = True

    if sistema_siempre_inestable:
        lineas.append("Para estabilidad: No existe ningún rango de K (hay elementos constantes <= 0 en la primera columna).\n")
    else:
        try:
            rango = sp.reduce_inequalities(inecuaciones, K_sym)
            try:
                conjunto = rango.as_set()
                rango_legible = _formatear_rango_k(conjunto, K_sym)
                lineas.append(f"Para estabilidad: {rango_legible}\n")
            except Exception:
                rango_str = str(rango).replace('&', 'y').replace('|', 'o')
                lineas.append(f"Para estabilidad: {rango_str}\n")
        except Exception as e:
            lineas.append(f"No se pudo resolver el rango de estabilidad: {e}\n")

    resultado_str = "\n".join(lineas)
    print(resultado_str)
    
    return condiciones, resultado_str

def _construir_tabla(coeficientes_k, n):
    fila_par = list(coeficientes_k[0::2])
    fila_impar = list(coeficientes_k[1::2])

    max_cols = max(len(fila_par), len(fila_impar))
    fila_par += [sp.Integer(0)] * (max_cols - len(fila_par))
    fila_impar += [sp.Integer(0)] * (max_cols - len(fila_impar))

    tabla = [fila_par, fila_impar]

    for _ in range(n - 1):
        fila_ant = tabla[-2]
        fila_act = tabla[-1]
        pivot = fila_act[0]

        if sp.simplify(pivot) == 0:
            print("[!] Pivot cero con K simbolico")
            pivot = sp.Symbol('epsilon')

        nueva_fila = []
        for j in range(len(fila_ant) - 1):
            a, b = fila_ant[0], fila_act[0]
            c = fila_ant[j + 1] if j + 1 < len(fila_ant) else sp.Integer(0)
            d = fila_act[j + 1] if j + 1 < len(fila_act) else sp.Integer(0)
            
            elemento = sp.simplify(-(a * d - b * c) / b)
            nueva_fila.append(elemento)

        tabla.append(nueva_fila)

    return tabla

def _formatear_rango_k(conjunto, K):
    if conjunto == sp.EmptySet:
        return "No existe ningún rango de K que haga el sistema estable."
    if conjunto == sp.Reals:
        return "Cualquier valor real (K ∈ ℝ)"
    
    if isinstance(conjunto, sp.Union):
        partes = [_formatear_rango_k(arg, K) for arg in conjunto.args]
        return " o ".join(partes)
    
    if isinstance(conjunto, sp.Interval):
        inf, sup = conjunto.inf, conjunto.sup
        incl_inf = conjunto.left_open == False
        incl_sup = conjunto.right_open == False
        
        op_inf = "<=" if incl_inf else "<"
        op_sup = "<=" if incl_sup else "<"
        
        if inf == sp.S.NegativeInfinity and sup == sp.S.Infinity:
            return "Cualquier valor real"
        elif inf == sp.S.NegativeInfinity:
            return f"K {op_sup} {sup}"
        elif sup == sp.S.Infinity:
            op = ">=" if incl_inf else ">"
            return f"K {op} {inf}"
        else:
            return f"{inf} {op_inf} K {op_sup} {sup}"
            
    return str(conjunto)