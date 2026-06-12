# Cálculos matemáticos de sistemas de control
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES

import numpy as np
import scipy.signal as signal

def calcular_raices(coeficientes):
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
        "valor_final": 0.0,
        "error_estado_estable_pct": 0.0,
        "ts_val": None
    }
    
    # Valor final ante entrada escalón
    if coef_den[-1] != 0:
        val_final = (coef_num[-1] / coef_den[-1]) * amplitud_escalon
        resultados["valor_final"] = val_final
        if amplitud_escalon != 0:
            resultados["error_estado_estable_pct"] = (abs(amplitud_escalon - val_final) / abs(amplitud_escalon)) * 100
    else:
        resultados["valor_final"] = float('inf')
        resultados["error_estado_estable_pct"] = float('inf')
        
    if len(polos) == 0 or analizar_estabilidad(polos) != "Estable":
        return resultados

    polos_ordenados = sorted(polos, key=lambda p: abs(np.real(p)))
    min_real = abs(np.real(polos_ordenados[0]))
    
    # Lógica de dominancia basada en el criterio de relación de polos (> 5)
    if len(polos) == 1:
        resultados["dominancia"] = "Sistema de Primer Orden"
    elif len(polos) >= 2:
        ratio = abs(np.real(polos_ordenados[1]) / np.real(polos_ordenados[0])) if min_real != 0 else 0
        resultados["dominancia"] = "Primer Orden Dominante" if ratio > 5 else "Segundo Orden (o superior)"

    # Tiempo de estabilización aproximado (criterio del 2%)
    ts = 4.0 / min_real if min_real > 0 else float('inf')
    resultados["tiempo_estabilizacion"] = f"{ts:.3g} segundos"
    resultados["ts_val"] = ts
    
    return resultados

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
            
        pico_max = np.max(y)
        sobreimpulso = (((pico_max - vf) / vf) * 100) if (pico_max > vf and vf > 0) else 0.0
        resultados["sobreimpulso"] = f"{sobreimpulso:.2f}%"
        
        if sobreimpulso > 0:
            resultados["tiempo_pico"] = f"{t[np.argmax(y)]:.3g} s"
            
        # Tiempo de subida (10% a 90% del valor final)
        if vf > 0:
            idx_10 = np.where(y >= 0.1 * vf)[0]
            idx_90 = np.where(y >= 0.9 * vf)[0]
            if len(idx_10) > 0 and len(idx_90) > 0:
                resultados["tiempo_subida"] = f"{t[idx_90[0]] - t[idx_10[0]]:.3g} s"
    except Exception:
        pass
        
    return resultados

def obtener_lazo_cerrado(num_g, den_g, tipo_control, kp, ki, H=1.0):
    # Retorna: (num_referencia, num_perturbacion, den_cerrado)
    if tipo_control.upper() == 'PI':
        num_c = np.array([kp, ki])
        den_c = np.array([1, 0])
    else:  # P
        num_c = np.array([kp])
        den_c = np.array([1])
        
    # C(s)*G(s)
    num_ol = np.polymul(num_c, num_g)
    den_ol = np.polymul(den_c, den_g)
    
    # Denominador común de lazo cerrado (1 + H * C(s)*G(s))
    den_cl = np.polyadd(den_ol, H * num_ol)
    
    # Numerador R(s) -> Y(s)
    num_cl_ref = num_ol
    
    # Numerador D(s) -> Y(s) (perturbación en la entrada de la planta)
    num_cl_dist = np.polymul(num_g, den_c)
    
    return list(num_cl_ref), list(num_cl_dist), list(den_cl)

def simular_escalon(coef_num, coef_den, amplitud):
    sys = signal.TransferFunction(coef_num, coef_den)
    t, y = signal.step(sys, N=2000)
    return t, y * amplitud

def simular_rampa(coef_num, coef_den, amplitud, t_sim=None):
    sys = signal.TransferFunction(coef_num, coef_den)
    if t_sim is None:
        polos = np.roots(coef_den)
        max_real = np.max(np.real(polos)) if len(polos) > 0 else 0
        
        if max_real < -1e-5:
            partes_reales = np.abs(np.real(polos))
            min_real = np.min(partes_reales[partes_reales > 1e-9]) if any(partes_reales > 1e-9) else 1.0
            t_sim = 4.0 / min_real * 2.5
        else:
            t_sim = 15.0
            
    t = np.linspace(0, t_sim, 2000)
    t_out, y_out, _ = signal.lsim(sys, U=amplitud * t, T=t)
    return t_out, y_out

def simular_pulso(coef_num, coef_den, amplitud, ancho_pulso, retardo, t_sim=None):
    sys = signal.TransferFunction(coef_num, coef_den)
    if t_sim is None:
        # Mostramos 2 periodos completos más el retardo
        t_sim = retardo + 2.0 * (2.0 * ancho_pulso)
        
    t = np.linspace(0, t_sim, 2000)
    u = np.zeros_like(t)
    
    # Construir el tren de pulsos (onda cuadrada) con retardo
    periodo = 2.0 * ancho_pulso
    for i, ti in enumerate(t):
        if ti >= retardo:
            t_rel = ti - retardo
            if (t_rel % periodo) < ancho_pulso:
                u[i] = amplitud
                
    t_out, y_out, _ = signal.lsim(sys, U=u, T=t)
    return t_out, y_out, u