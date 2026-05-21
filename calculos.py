import numpy as np
import scipy.signal as signal

def formatear_numero(num):
    # Aquí muestro resultados con 3 cifras significativas (Inciso 3c)
    if np.iscomplex(num):
        return f"{num.real:.3g} {num.imag:+.3g}j"
    return f"{num.real:.3g}"

def calcular_raices(coeficientes):
    # CORRECCIÓN: Usamos len() para evitar errores de ambigüedad con arreglos de NumPy
    if len(coeficientes) == 0 or (len(coeficientes) == 1 and coeficientes[0] == 0):
        return np.array([])
    return np.roots(coeficientes)

def analizar_estabilidad(polos):
    if len(polos) == 0:
        return "Estable"
    
    max_real = np.max(np.real(polos))
    
    if max_real > 0:
        return "Inestable"
    elif np.isclose(max_real, 0):
        return "Marginalmente Estable"
    else:
        return "Estable"

def analizar_dominancia_y_escalon(polos, coef_num, coef_den, amplitud_escalon=1.0):
    resultados = {
        "dominancia": "No determinable",
        "tiempo_estabilizacion": "Infinito (Inestable)",
        "valor_final": 0.0
    }
    
    # Aquí calculo el valor final ante una entrada escalón (escalada por la amplitud)
    if coef_den[-1] != 0:
        resultados["valor_final"] = (coef_num[-1] / coef_den[-1]) * amplitud_escalon
    else:
        resultados["valor_final"] = float('inf')
        
    if len(polos) == 0 or analizar_estabilidad(polos) != "Estable":
        return resultados

    partes_reales = np.abs(np.real(polos))
    polos_ordenados = sorted(polos, key=lambda p: abs(np.real(p)))
    min_real = abs(np.real(polos_ordenados[0]))
    
    # Nueva lógica de dominancia basada en el ratio > 5 (Inciso 3f modificado)
    if len(polos) == 1:
        resultados["dominancia"] = "Sistema de Primer Orden"
    elif len(polos) >= 2:
        # Evitar división por cero
        if min_real == 0:
            ratio = 0
        else:
            ratio = abs(np.real(polos_ordenados[1]) / np.real(polos_ordenados[0]))
            
        if ratio > 5:
            resultados["dominancia"] = "Primer Orden Dominante"
        else:
            resultados["dominancia"] = f"Segundo Orden (o superior)"

    # Aquí muestro el tiempo de estabilización del sistema (Inciso 3g)
    ts = 4.0 / min_real if min_real > 0 else float('inf')
    resultados["tiempo_estabilizacion"] = f"{ts:.3g} segundos"
    
    return resultados

def obtener_superindice(numero):
    """Convierte un número normal a su versión en superíndice Unicode."""
    superindices = {'0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴', 
                    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹', '-': '⁻'}
    return "".join(superindices.get(digito, digito) for digito in str(numero))

def construir_polinomio(coeficientes):
    """Convierte una lista de coeficientes en un texto de polinomio con formato visual."""
    if len(coeficientes) == 0:
        return "0"
    
    grado = len(coeficientes) - 1
    terminos = []
    
    for i, c in enumerate(coeficientes):
        if c == 0 and grado != 0: 
            continue
            
        potencia = grado - i
        c_str = f"{c:g}"
        
        # Ocultar el "1" si acompaña a una s
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
        
    polinomio = " + ".join(terminos)
    return polinomio.replace("+ -", "- ")

def analizar_transitorio(coef_num, coef_den, amplitud_escalon=1.0):
    resultados = {
        "tiempo_subida": "N/A",
        "tiempo_pico": "N/A",
        "sobreimpulso": "N/A"
    }
    try:
        sys = signal.TransferFunction(coef_num, coef_den)
        t, y = signal.step(sys, N=2000)
        y = y * amplitud_escalon
        
        vf = y[-1]
        if abs(vf) < 1e-9:
            return resultados
            
        # Sobreimpulso (%)
        pico_max = np.max(y)
        if pico_max > vf and vf > 0:
            sobreimpulso = ((pico_max - vf) / vf) * 100
        else:
            sobreimpulso = 0.0
            
        resultados["sobreimpulso"] = f"{sobreimpulso:.2f}%"
        
        # Tiempo pico
        if sobreimpulso > 0:
            idx_pico = np.argmax(y)
            resultados["tiempo_pico"] = f"{t[idx_pico]:.3g} s"
            
        # Tiempo de subida (10% a 90%)
        if vf > 0:
            idx_10 = np.where(y >= 0.1 * vf)[0]
            idx_90 = np.where(y >= 0.9 * vf)[0]
            if len(idx_10) > 0 and len(idx_90) > 0:
                t_10 = t[idx_10[0]]
                t_90 = t[idx_90[0]]
                resultados["tiempo_subida"] = f"{t_90 - t_10:.3g} s"
    except Exception:
        pass
        
    return resultados