import calculos
import graficas
import numpy as np
import os
from datetime import datetime

def leer_coeficiente(mensaje):
    """Asegura que los coeficientes sean números reales válidos."""
    while True:
        try:
            valor = float(input(mensaje))
            return valor
        except ValueError:
            print("Error: Debes ingresar un número real válido. Intenta de nuevo.")

def main():
    if not os.path.exists("Resultados"):
        os.makedirs("Resultados")

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n=== Análisis de Funciones de Transferencia (Lazo Abierto vs Cerrado) ===")
        
        # Solicitar amplitud del escalón
        try:
            amp_str = input("Ingresa la amplitud del escalón (presiona Enter para 1.0): ")
            amplitud = float(amp_str) if amp_str.strip() else 1.0
        except ValueError:
            print("Valor no válido, se usará amplitud = 1.0")
            amplitud = 1.0
            
        # Validación de grados: n <= m
        while True:
            try:
                grado_num = int(input("Ingresa el grado del numerador (n): "))
                grado_den = int(input("Ingresa el grado del denominador (m): "))
                
                if grado_den == 0:
                    print("Error: El denominador debe ser de al menos grado 1.")
                elif grado_num > grado_den:
                    print("Error: El grado del numerador (n) no puede ser mayor al del denominador (m).")
                else:
                    break
            except ValueError:
                print("Error: Ingresa un número entero.")

        print("\n--- Coeficientes del Numerador ---")
        coef_num = []
        for i in range(grado_num + 1):
            potencia = grado_num - i
            super_pot = calculos.obtener_superindice(potencia)
            coef_num.append(leer_coeficiente(f"Coeficiente de s{super_pot}: "))
            
        print("\n--- Coeficientes del Denominador ---")
        coef_den = []
        for i in range(grado_den + 1):
            potencia = grado_den - i
            super_pot = calculos.obtener_superindice(potencia)
            coef_den.append(leer_coeficiente(f"Coeficiente de s{super_pot}: "))
        
        # Construcción visual de la FT original
        str_num = calculos.construir_polinomio(coef_num)
        str_den = calculos.construir_polinomio(coef_den)
        longitud_linea = max(len(str_num), len(str_den))
        
        reporte = []
        reporte.append("\n" + "="*40)
        reporte.append("      Función de Transferencia G(s)")
        reporte.append("="*40)
        reporte.append(f"{str_num.center(40)}")
        reporte.append(f"{('-' * longitud_linea).center(40)}")
        reporte.append(f"{str_den.center(40)}")
        reporte.append("="*40)
            
        # Cálculos para lazo abierto (Original)
        ceros = calculos.calcular_raices(coef_num) if grado_num > 0 else []
        polos = calculos.calcular_raices(coef_den)
        
        estado_sistema = calculos.analizar_estabilidad(polos)
        analisis_la = calculos.analizar_dominancia_y_escalon(polos, coef_num, coef_den, amplitud)
        transitorio_la = calculos.analizar_transitorio(coef_num, coef_den, amplitud)

        reporte.append("\n=== Resultados (Lazo Abierto / Original) ===")
        reporte.append(f">> ESTADO: {estado_sistema.upper()}")
        reporte.append(f">> DOMINANCIA: {analisis_la['dominancia']}")
        reporte.append(f">> TIEMPO ESTAB.: {analisis_la['tiempo_estabilizacion']}")
        reporte.append(f">> VALOR FINAL: {calculos.formatear_numero(analisis_la['valor_final'])}")
        reporte.append(f">> SOBREIMPULSO (Mp): {transitorio_la['sobreimpulso']}")
        reporte.append(f">> TIEMPO PICO (Tp): {transitorio_la['tiempo_pico']}")
        reporte.append(f">> TIEMPO SUBIDA (Tr): {transitorio_la['tiempo_subida']}")
        
        # --- PROCESAMIENTO DE LAZO CERRADO ---
        coef_den_cerrado = np.polyadd(coef_num, coef_den)
        polos_cerrado = calculos.calcular_raices(coef_den_cerrado)
        analisis_lc = calculos.analizar_dominancia_y_escalon(polos_cerrado, coef_num, coef_den_cerrado, amplitud)

        estado_sistema_lc = calculos.analizar_estabilidad(polos_cerrado)
        transitorio_lc = calculos.analizar_transitorio(coef_num, coef_den_cerrado, amplitud)

        reporte.append("\n=== Resultados (Lazo Cerrado) ===")
        reporte.append(f">> ESTADO: {estado_sistema_lc.upper()}")
        reporte.append(f">> DOMINANCIA: {analisis_lc['dominancia']}")
        reporte.append(f">> TIEMPO ESTAB.: {analisis_lc['tiempo_estabilizacion']}")
        reporte.append(f">> VALOR FINAL: {calculos.formatear_numero(analisis_lc['valor_final'])}")
        reporte.append(f">> SOBREIMPULSO (Mp): {transitorio_lc['sobreimpulso']}")
        reporte.append(f">> TIEMPO PICO (Tp): {transitorio_lc['tiempo_pico']}")
        reporte.append(f">> TIEMPO SUBIDA (Tr): {transitorio_lc['tiempo_subida']}")
        reporte.append("="*40)
        
        texto_reporte = "\n".join(reporte)
        print(texto_reporte)
        
        # --- GENERACIÓN DE GRÁFICAS Y GUARDADO ---
        print("\nGenerando gráficas y guardando resultados...")
        
        ts = datetime.now().strftime("%d-%m-%Y_%H-%M")
        ruta_txt = os.path.join("Resultados", f"{ts}_resultados.txt")
        ruta_pz = os.path.join("Resultados", f"{ts}_polos-y-ceros.png")
        ruta_lazos = os.path.join("Resultados", f"{ts}_lazos.png")
        
        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write("REPORTE DE SISTEMA DE CONTROL\n")
            f.write(f"Fecha y Hora: {ts}\n")
            f.write(texto_reporte)
        
        # 1. Ventana de Mapa de Polos y Ceros (Original)
        graficas.graficar_pz(ceros, polos, estado_sistema, ruta_guardado=ruta_pz)
        
        # 2. Ventana de Comparación de Escalón (Abierto vs Cerrado)
        graficas.graficar_escalon(coef_num, coef_den, coef_num, coef_den_cerrado, amplitud, ruta_lazos=ruta_lazos)

        print(f"\n¡Análisis guardado exitosamente en la carpeta 'Resultados' con el prefijo {ts}!")
        
        # Preguntar por otro sistema
        resp = input("\n¿Desea analizar otro sistema? (s/n): ").strip().lower()
        if resp != 's':
            print("Cerrando programa...")
            break

if __name__ == "__main__":
    main()