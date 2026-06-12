## III. DESCRIPCIÓN DEL PROGRAMA

Para simular y sintonizar nuestro sistema de control, programamos una herramienta modular en Python. Dividimos el código en archivos para que cada uno tenga una tarea clara y única:

```
[ main.py ] (Código principal)
    │
    ├──> [ calculos.py ] (Matemáticas y simulaciones LTI)
    ├──> [ graficas.py ] (Dibujo de curvas y marcas)
    ├──> [ routh.py ]    (Tabla de Routh simbólica)
    ├──> [ reporte.py ]  (Formateador y exportador de datos)
    └──> [ utils.py ]    (Utilidades de texto)
```

### A. Organización y Responsabilidad de cada Módulo

1. **`main.py` (La Interfaz y el Flujo)**: Es el administrador central del programa. Se encarga de mostrar los menús en la consola y pedirnos los datos de la planta (grados y coeficientes de la transferencia) y la configuración de prueba (tipo de entrada, amplitud, perturbaciones y ganancias $K_p$ y $K_i$). Tiene un bucle dinámico especial para cambiar el valor de $K_p$ y simularlo al instante sin tener que volver a escribir todos los valores de nuevo.
2. **`calculos.py` (El Cerebro Matemático)**: Realiza todos los cálculos matemáticos del sistema utilizando las librerías `numpy` y `scipy.signal`. Calcula los polos y ceros, determina si el sistema es estable, obtiene la dominancia de polos y las métricas transitorias (sobreimpulso, tiempo de asentamiento y subida). También contiene el álgebra de polinomios para cerrar el lazo del controlador ($P$ o $PI$) y las funciones que corren las simulaciones físicas reales ante escalón, rampa o tren de pulsos.
3. **`graficas.py` (El Visualizador)**: Recibe los vectores de tiempo y respuesta ya simulados y dibuja las curvas utilizando `matplotlib`. Muestra juntas la señal de referencia ideal (en color gris), la respuesta de lazo abierto (azul) y la de lazo cerrado (naranja). Además, para facilitar el análisis del control, grafica automáticamente una línea vertical punteada en el tiempo de asentamiento ($t_s$) de cada curva y marca el punto exacto donde ocurre el pico máximo de sobreimpulso. Si se activa la perturbación, genera un segundo gráfico independiente mostrando cómo el sistema la rechaza.
4. **`routh.py` (El Analizador de Routh-Hurwitz)**: Es el encargado de la sintonización analítica. Utiliza la librería simbólica `sympy` para construir la tabla de Routh dejando la ganancia como la variable simbólica $K$. Revisa los elementos de la primera columna y resuelve las inecuaciones para decirnos en qué rango exacto de ganancia el sistema es estable.
5. **`reporte.py` (El Generador de Reportes)**: Toma las ecuaciones polinomiales y los resultados calculados, les da un formato visual limpio y ordenado, y los exporta automáticamente a un archivo `.txt` en la carpeta `Resultados`, junto con las imágenes `.png` de las gráficas.
6. **`utils.py` (El Asistente de Formato)**: Contiene utilidades auxiliares de texto para que las fórmulas y números se vean ordenados y legibles. Por ejemplo, convierte los exponentes normales a superíndices Unicode (mostrando $s² + 5s$ en lugar de `s^2 + 5*s`).

### B. Ejemplo Práctico de Funcionamiento (Con nuestro Motor)

#### 1. Entrada de datos de la planta
Iniciamos el programa e ingresamos los coeficientes de la función de transferencia de nuestro motor $G(s) = \frac{103.25}{s^2 + 59.28s}$ (Numerador: `[103.25]`, Denominador: `[1, 59.28, 0]`) en `main.py`. Además, seleccionamos la entrada de **Escalón Unitario** (amplitud $1.0$) y perturbación de $1.0$.

#### 2. Análisis de Lazo Abierto
El programa deduce automáticamente los polos en lazo abierto ($p_1 = 0$, $p_2 = -59.28$) mediante `calculos.py`. Nos indica que el sistema es **Marginalmente Estable** y divergería ante un escalón de voltaje continuo.

#### 3. Sintonización simbólica por Routh-Hurwitz
Ejecutamos el análisis en `routh.py` para el polinomio característico $s^2 + 59.28s + 103.25K = 0$. El programa resuelve simbólicamente la primera columna y nos indica que el sistema cerrado es estable para **cualquier $K_p > 0$**.

#### 4. Cálculo del Lazo Cerrado
Seleccionamos y cargamos una ganancia proporcional **$K_p = 60$**. El programa calcula la función de lazo cerrado $T(s) = \frac{6195}{s^2 + 59.28s + 6195}$, cuyos polos se ubican en $-29.64 \pm j73.07$.

#### 5. Simulación temporal y gráficos
Simulamos el sistema con `scipy` y se despliega el gráfico comparativo en `graficas.py`. Visualizamos la respuesta al escalón con un sobreimpulso de **$22.75\%$** y tiempo de asentamiento de **$t_s = 0.135\text{ s}$** (indicado con línea vertical naranja). El panel secundario muestra el rechazo de la perturbación regresando a cero.

#### 6. Reporte final
El módulo `reporte.py` da formato con `utils.py` (ej. $s^2 \to s²$) y guarda automáticamente el reporte `.txt` y las gráficas `.png` en la carpeta `Resultados/`.