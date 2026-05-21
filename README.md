# Programa Control Analógico I - Equipo 8

**Integrantes:**
- Moisés Moreno Cortez
- Kassandra Delgado Mendez
- Luz Selena
- Luis Mendoza

---

## Descripción
Este programa es una herramienta unificada y robusta para el análisis de sistemas de control analógico. Combina diversas funciones matemáticas para evaluar sistemas tanto en **Lazo Abierto** como en **Lazo Cerrado**, ofreciendo reportes numéricos y visuales de forma automatizada.

## ¿Qué calcula el programa?
Al ingresar la función de transferencia de un sistema, el programa determina:
- **Estabilidad**: Estable, Marginalmente Estable o Inestable.
- **Dominancia**: Clasificación del orden dominante del sistema (usando proporción de polos reales).
- **Análisis Transitorio**:
  - Tiempo de Estabilización ($T_s$) al 2%.
  - Valor Final (Estado Estable).
  - Sobreimpulso ($M_p$ / %OS).
  - Tiempo Pico ($T_p$).
  - Tiempo de Subida ($T_r$).
- **Gráficas Visuales**: 
  - Mapa de Polos y Ceros.
  - Comparativa de respuesta al escalón marcando visualmente los picos (sobreimpulsos) y el valor final (asíntotas).

## ¿Cómo usarlo?

### 1. Ejecución
Abre tu terminal en la carpeta del programa y ejecuta:
```bash
python main.py
```

### 2. Ingreso de Datos
El programa es muy interactivo. Te irá guiando paso a paso:
1. **Amplitud**: Ingresa la amplitud de tu señal escalón (si presionas `Enter`, se asume `1.0`).
2. **Grados**: Ingresa el grado polinomial mayor de tu numerador (n) y denominador (m).
3. **Coeficientes**: Ingresa cada coeficiente de $s$ desde la potencia mayor hasta $s^0$.

### 3. Resultados Automáticos
Al terminar, verás los resultados matemáticos en tu consola y se desplegarán dos ventanas con las gráficas de tu sistema. 

Además, se generará una carpeta llamada `Resultados` dentro del mismo directorio. Por cada sistema que analices, ahí se guardará un respaldo automático con la fecha y hora exacta:
- `[fecha]_resultados.txt` (Todos los números y métricas).
- `[fecha]_polos-y-ceros.png` (Imagen de la gráfica de polos).
- `[fecha]_lazos.png` (Imagen de la gráfica transitoria).
