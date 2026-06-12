# Programa Principal — Análisis de Sistemas de Control
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES
# Facultad de Ingeniería Eléctrica - Ingeniería en Computación

import os
from datetime import datetime
import calculos
import graficas
import reporte
from utils import obtener_superindice

def leer_coeficiente(mensaje):
    while True:
        try:
            return float(input(mensaje))
        except ValueError:
            print("Error: Debes ingresar un número real válido. Intenta de nuevo.")

def leer_float(mensaje, default=1.0):
    try:
        texto = input(mensaje)
        return float(texto) if texto.strip() else default
    except ValueError:
        print(f"Valor no válido, se usará {default}")
        return default

def leer_opcion(mensaje, opciones_validas, default=None):
    texto = input(mensaje).strip()
    if not texto and default is not None:
        return default
    return texto if texto in opciones_validas else default

def leer_planta():
    while True:
        try:
            grado_num = int(input("\nIngresa el grado del numerador del sistema G(s) (n): "))
            grado_den = int(input("Ingresa el grado del denominador del sistema G(s) (m): "))
            
            if grado_den == 0:
                print("Error: El denominador debe ser de al menos grado 1.")
            elif grado_num > grado_den:
                print("Error: El grado del numerador (n) no puede ser mayor al del denominador (m).")
            else:
                break
        except ValueError:
            print("Error: Ingresa un número entero.")

    print("\n--- Coeficientes del Numerador ---")
    coef_num = [leer_coeficiente(f"Coeficiente de s{obtener_superindice(grado_num - i)}: ") for i in range(grado_num + 1)]
        
    print("\n--- Coeficientes del Denominador ---")
    coef_den = [leer_coeficiente(f"Coeficiente de s{obtener_superindice(grado_den - i)}: ") for i in range(grado_den + 1)]

    return coef_num, coef_den, grado_num

def leer_configuracion():
    print("\nSeleccione el tipo de entrada:")
    print("1. Escalón")
    print("2. Rampa")
    print("3. Tren de Pulsos (Onda Cuadrada)")
    opc = leer_opcion("Opción (1-3, presiona Enter para Escalón): ", ["1", "2", "3"], "1")
    
    if opc == "2":
        tipo_entrada = "Rampa"
    elif opc == "3":
        tipo_entrada = "Tren de Pulsos"
    else:
        tipo_entrada = "Escalón"

    nombre_amp = "pendiente" if tipo_entrada == "Rampa" else "amplitud"
    amplitud = leer_float(f"Ingresa la {nombre_amp} (presiona Enter para 1.0): ")

    ancho_pulso = 5.0
    retardo = 1.0
    if tipo_entrada == "Tren de Pulsos":
        ancho_pulso = leer_float("Ingresa el ancho de pulso (duración en alto, presiona Enter para 5.0): ", default=5.0)
        retardo = leer_float("Ingresa el retardo de inicio (presiona Enter para 1.0): ", default=1.0)

    print("\nSeleccione el tipo de controlador en Lazo Cerrado:")
    print("1. P (Proporcional)")
    print("2. PI (Proporcional-Integral)")
    opc = leer_opcion("Opción (1-2, presiona Enter para P): ", ["1", "2"], "1")
    tipo_control = "PI" if opc == "2" else "P"
    
    kp = leer_float("Ingresa la ganancia Kp (presiona Enter para 1.0): ")
    ki = 0.0
    if tipo_control == "PI":
        ki = leer_float("Ingresa la ganancia Ki (presiona Enter para 1.0): ")

    H = leer_float("Ingresa la ganancia de retroalimentación H (presiona Enter para 1.0): ", default=1.0)

    simular_dist = input("\n¿Desea simular una perturbación de escalón en la entrada del sistema? (s/N): ").strip().lower() == 's'
    amp_dist = leer_float("Ingresa la amplitud de la perturbación (presiona Enter para 1.0): ") if simular_dist else 0.0

    return tipo_entrada, amplitud, tipo_control, kp, ki, H, simular_dist, amp_dist, ancho_pulso, retardo

def ejecutar_routh(coef_num, coef_den):
    resp = input("\n¿Desea realizar el análisis de Routh-Hurwitz para sintonizar Kp simbólicamente? (s/N): ").strip().lower()
    if resp != 's':
        return ""
    
    try:
        import sympy as sp
        from routh import analizar_con_k
        
        K_sym = sp.Symbol('K', real=True)
        len_diff = len(coef_den) - len(coef_num)
        coef_num_padded = [0] * len_diff + list(coef_num)
        coef_k = [sp.simplify(d + K_sym * n) for d, n in zip(coef_den, coef_num_padded)]
        
        print("\n--- Iniciando análisis simbólico Routh-Hurwitz ---")
        condiciones, routh_str = analizar_con_k(coef_k)
        input("\nPresiona Enter para continuar con la simulación...")
        return routh_str
    except Exception as e:
        print(f"Error al ejecutar sintonización simbólica: {e}")
        input("\nPresiona Enter para continuar...")
        return ""

def simular_sistema(coef_num, coef_den, coef_num_cerrado, coef_den_cerrado,
                    coef_dist_cerrado, tipo_entrada, amplitud, simular_dist, amp_dist,
                    ancho_pulso=5.0, retardo=1.0):
    u_ref = None
    if tipo_entrada == "Rampa":
        t_la, y_la = calculos.simular_rampa(coef_num, coef_den, amplitud)
        t_lc, y_lc = calculos.simular_rampa(coef_num_cerrado, coef_den_cerrado, amplitud, t_sim=t_la[-1])
    elif tipo_entrada == "Tren de Pulsos":
        t_la, y_la, _ = calculos.simular_pulso(coef_num, coef_den, amplitud, ancho_pulso, retardo)
        t_lc, y_lc, u_ref = calculos.simular_pulso(coef_num_cerrado, coef_den_cerrado, amplitud, ancho_pulso, retardo, t_sim=t_la[-1])
    else:
        t_la, y_la = calculos.simular_escalon(coef_num, coef_den, amplitud)
        t_lc, y_lc = calculos.simular_escalon(coef_num_cerrado, coef_den_cerrado, amplitud)

    t_dist, y_dist = None, None
    if simular_dist:
        t_dist, y_dist = calculos.simular_escalon(coef_dist_cerrado, coef_den_cerrado, amp_dist)

    return t_la, y_la, t_lc, y_lc, t_dist, y_dist, u_ref

def main():
    if not os.path.exists("Resultados"):
        os.makedirs("Resultados")

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n=== Análisis de Funciones de Transferencia (Lazo Abierto vs Cerrado) ===")
        
        tipo_entrada, amplitud, tipo_control, kp, ki, H, simular_dist, amp_dist, ancho_pulso, retardo = leer_configuracion()
        coef_num, coef_den, grado_num = leer_planta()
        
        routh_str = ""
        if tipo_control == "P":
            routh_str = ejecutar_routh(coef_num, coef_den)

        # Análisis de lazo abierto
        ceros = calculos.calcular_raices(coef_num) if grado_num > 0 else []
        polos = calculos.calcular_raices(coef_den)
        estado_la = calculos.analizar_estabilidad(polos)
        analisis_la = calculos.analizar_dominancia_y_escalon(polos, coef_num, coef_den, amplitud)
        analisis_la['estado'] = estado_la
        transitorio_la = calculos.analizar_transitorio(coef_num, coef_den, amplitud)

        # Bucle interno de ganancias Kp/Ki
        while True:
            coef_num_cerrado, coef_dist_cerrado, coef_den_cerrado = calculos.obtener_lazo_cerrado(
                coef_num, coef_den, tipo_control, kp, ki, H=H
            )
            polos_cerrado = calculos.calcular_raices(coef_den_cerrado)
            estado_lc = calculos.analizar_estabilidad(polos_cerrado)
            analisis_lc = calculos.analizar_dominancia_y_escalon(polos_cerrado, coef_num_cerrado, coef_den_cerrado, amplitud)
            analisis_lc['estado'] = estado_lc
            transitorio_lc = calculos.analizar_transitorio(coef_num_cerrado, coef_den_cerrado, amplitud)

            # Construcción del reporte para el archivo (lleva Routh-Hurwitz)
            lineas_archivo = []
            lineas_archivo += reporte.construir_bloque_ft("Función de Transferencia G(s)", coef_num, coef_den)
            lineas_archivo += reporte.construir_resultados_lazo("Resultados (Lazo Abierto / Original)", analisis_la, transitorio_la)
            
            if routh_str:
                lineas_archivo.append("\n" + routh_str + "\n")
                
            lineas_archivo += reporte.construir_bloque_ft("Función de Transferencia Lazo Cerrado T(s)", coef_num_cerrado, coef_den_cerrado)
            
            extras_lc = {
                "CONTROLADOR": f"{tipo_control} (Kp = {kp}, Ki = {ki})",
                "RETROALIMENTACIÓN (H)": f"{H}",
                "ENTRADA": f"{tipo_entrada} (Amplitud/Pendiente = {amplitud})"
            }
            if simular_dist:
                extras_lc["PERTURBACIÓN DE ENTRADA"] = f"Escalón (Amplitud = {amp_dist})"
            lineas_archivo += reporte.construir_resultados_lazo("Resultados (Lazo Cerrado)", analisis_lc, transitorio_lc, extras_lc)
            lineas_archivo.append("="*40)
            
            # Construcción del reporte para pantalla de consola (sin repetir Routh)
            lineas_consola = []
            lineas_consola += reporte.construir_bloque_ft("Función de Transferencia G(s)", coef_num, coef_den)
            lineas_consola += reporte.construir_resultados_lazo("Resultados (Lazo Abierto / Original)", analisis_la, transitorio_la)
            lineas_consola += reporte.construir_bloque_ft("Función de Transferencia Lazo Cerrado T(s)", coef_num_cerrado, coef_den_cerrado)
            lineas_consola += reporte.construir_resultados_lazo("Resultados (Lazo Cerrado)", analisis_lc, transitorio_lc, extras_lc)
            lineas_consola.append("="*40)
            
            texto_consola = "\n".join(lineas_consola)
            print(texto_consola)
            
            # Guardado de reporte
            print("\nGenerando gráficas y guardando resultados...")
            ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            ruta_txt = os.path.join("Resultados", f"{ts}_resultados.txt")
            ruta_pz  = os.path.join("Resultados", f"{ts}_polos-y-ceros.png")
            ruta_lazos = os.path.join("Resultados", f"{ts}_lazos.png")
            
            texto_archivo = "\n".join(lineas_archivo)
            reporte.guardar_reporte(ruta_txt, ts, texto_archivo)
            
            t_la, y_la, t_lc, y_lc, t_dist, y_dist, u_ref = simular_sistema(
                coef_num, coef_den, coef_num_cerrado, coef_den_cerrado,
                coef_dist_cerrado, tipo_entrada, amplitud, simular_dist, amp_dist,
                ancho_pulso=ancho_pulso, retardo=retardo
            )
            
            graficas.graficar_pz(ceros, polos, estado_la, ruta_guardado=ruta_pz)
            graficas.graficar_respuesta(
                t_la, y_la, t_lc, y_lc, tipo_entrada, amplitud,
                t_dist, y_dist, amp_dist,
                tipo_control=tipo_control, kp=kp, ki=ki, H=H,
                y_ref=u_ref,
                ts_la=analisis_la.get('ts_val'),
                ts_lc=analisis_lc.get('ts_val'),
                ruta_guardado=ruta_lazos
            )

            print(f"\n¡Análisis guardado exitosamente en la carpeta 'Resultados' con el prefijo {ts}!")

            resp_kp = input("\n¿Desea probar con otras ganancias/retroalimentación (mismo sistema)? (s/N): ").strip().lower()
            if resp_kp == 's':
                kp = leer_float(f"Ingresa el nuevo valor de Kp (actual {kp}): ", default=kp)
                if tipo_control == "PI":
                    ki = leer_float(f"Ingresa el nuevo valor de Ki (actual {ki}): ", default=ki)
                H = leer_float(f"Ingresa el nuevo valor de H (actual {H}): ", default=H)
            else:
                break

        resp = input("\n¿Desea analizar otro sistema? (s/n): ").strip().lower()
        if resp != 's':
            print("Cerrando programa...")
            break

if __name__ == "__main__":
    main()