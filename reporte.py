# Construcción y guardado de reportes de texto
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES

import os
from utils import construir_polinomio, formatear_numero

def construir_bloque_ft(titulo, coef_num, coef_den):
    # Genera una representación en texto estilizada de una función de transferencia
    str_num = construir_polinomio(coef_num)
    str_den = construir_polinomio(coef_den)
    longitud_linea = max(len(str_num), len(str_den))
    
    lineas = []
    lineas.append("\n" + "="*40)
    lineas.append(f"  {titulo}")
    lineas.append("="*40)
    lineas.append(str_num.center(40))
    lineas.append(('-' * longitud_linea).center(40))
    lineas.append(str_den.center(40))
    lineas.append("="*40)
    return lineas

def construir_resultados_lazo(titulo, analisis, transitorio, extras=None):
    # Genera la sección de texto con métricas de estabilidad y régimen transitorio
    lineas = []
    lineas.append(f"\n=== {titulo} ===")
    
    if extras:
        for k, v in extras.items():
            lineas.append(f">> {k}: {v}")
    
    lineas.append(f">> ESTADO: {analisis['estado'].upper()}")
    lineas.append(f">> DOMINANCIA: {analisis['dominancia']}")
    lineas.append(f">> TIEMPO ESTAB.: {analisis['tiempo_estabilizacion']}")
    lineas.append(f">> VALOR FINAL: {formatear_numero(analisis['valor_final'])}")
    if 'error_estado_estable_pct' in analisis:
        lineas.append(f">> ERROR ESTADO ESTABLE: {formatear_numero(analisis['error_estado_estable_pct'])}%")
    lineas.append(f">> SOBREIMPULSO (Mp): {transitorio['sobreimpulso']}")
    lineas.append(f">> TIEMPO PICO (Tp): {transitorio['tiempo_pico']}")
    lineas.append(f">> TIEMPO SUBIDA (Tr): {transitorio['tiempo_subida']}")
    return lineas

def guardar_reporte(ruta, timestamp, texto_reporte):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("REPORTE DE SISTEMA DE CONTROL\n")
        f.write(f"Fecha y Hora: {timestamp}\n")
        f.write(texto_reporte)