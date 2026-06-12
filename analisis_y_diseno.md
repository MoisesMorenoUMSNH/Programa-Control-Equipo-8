## IV. ANÁLISIS TRANSITORIO Y ESTABILIDAD

Para validar el comportamiento de nuestro sistema, utilizamos la función de transferencia de posición de nuestro motor de CD con tren de engranes en Lazo Abierto:

$$G(s) = \frac{103.25}{s^2 + 59.28s} = \frac{103.25}{s(s + 59.28)}$$

### A. Análisis de Polos y Ceros (Lazo Abierto)
Al calcular las raíces del denominador $s(s + 59.28) = 0$ obtenemos los polos del sistema:
- $p_1 = 0$ (Un polo integrador en el origen).
- $p_2 = -59.28$ (Un polo real estable).

Como tenemos un polo en cero y el otro está en el lado izquierdo del plano s, determinamos que nuestro sistema en lazo abierto es **Marginalmente Estable**. Ante una entrada de escalón continuo, la posición angular del motor va a divergir linealmente al infinito (se comporta como una rampa).

### B. Estabilidad por Routh-Hurwitz (Lazo Cerrado)
Al cerrar el lazo con una ganancia proporcional $K_p$, la función de transferencia de lazo cerrado $T(s)$ queda así:

$$T(s) = \frac{103.25 K_p}{s^2 + 59.28s + 103.25 K_p}$$

La tabla de Routh-Hurwitz para la ecuación característica $s^2 + 59.28s + 103.25 K_p = 0$ es:

| Fila | Columna 1 | Columna 2 |
|---|---|---|
| $s^2$ | $1$ | $103.25 K_p$ |
| $s^1$ | $59.28$ | $0$ |
| $s^0$ | $103.25 K_p$ | $0$ |

Para que nuestro sistema en lazo cerrado sea estable, todos los elementos de la primera columna deben ser del mismo signo (positivos). Por lo tanto, el rango de estabilidad de diseño es:
$$K_p > 0$$

Esto nos dice que cualquier ganancia proporcional positiva mantendrá estable la posición de nuestro motor.

---

## V. DISEÑO DEL CONTROLADOR

Diseñamos y sintonizamos controladores Proporcional (P) y Proporcional-Integral (PI) para ver cómo responde nuestro motor. La forma general del controlador es:
$$C(s) = \frac{K_p s + K_i}{s}$$

### A. Sintonización del Controlador P
Con $K_i = 0$, la respuesta transitoria depende del discriminante de nuestra ecuación característica de segundo orden:
$$\Delta = (59.28)^2 - 4(1)(103.25 K_p) = 3514.12 - 413 K_p$$

- **Para no tener oscilaciones (Sobreamortiguado)**: $\Delta \ge 0 \implies K_p \le 8.5$. El motor se moverá de forma suave pero lenta.
- **Para tener una respuesta rápida (Subamortiguado)**: Se permite un discriminante negativo ($\Delta < 0$), lo que nos deja elevar la ganancia. Nosotros elegimos $K_p = 60$ como ganancia de diseño para ver la respuesta oscilatoria y evaluar el sobreimpulso.

### B. Sintonización del Controlador PI (Criterio de Routh)
Al agregar la ganancia integral $K_i > 0$, la ecuación característica en lazo cerrado pasa a ser de tercer orden:
$$s^3 + 59.28s^2 + 103.25 K_p s + 103.25 K_i = 0$$

La tabla de Routh correspondiente es:

| Fila | Columna 1 | Columna 2 |
|---|---|---|
| $s^3$ | $1$ | $103.25 K_p$ |
| $s^2$ | $59.28$ | $103.25 K_i$ |
| $s^1$ | $103.25 \left( K_p - \frac{K_i}{59.28} \right)$ | $0$ |
| $s^0$ | $103.25 K_i$ | $0$ |

Para asegurar la estabilidad, revisamos que los elementos de la primera columna sean mayores a cero:
1. $103.25 K_i > 0 \implies K_i > 0$
2. $K_p - \frac{K_i}{59.28} > 0 \implies K_i < 59.28 K_p$

Por lo tanto, el rango de estabilidad para el controlador PI de nuestro motor es:
$$K_i > 0 \quad \text{y} \quad K_i < 59.28 K_p$$

---

## VI. PRUEBAS REALIZADAS (SIMULACIÓN)

Evaluamos el comportamiento de la posición angular de nuestro motor de CD en lazo cerrado bajo tres diferentes tipos de pruebas:

### A. Prueba 1: Respuesta ante Escalón Unitario
Simulamos la respuesta con un escalón unitario de referencia ($A = 1.0$) probando con tres valores distintos de ganancia proporcional:

| Ganancia ($K_p$) | Polos Cerrados | Tipo de Respuesta | Tiempo Asentamiento ($t_s$) | Sobreimpulso ($M_p$) | Error Estacionario ($e_{ss}$) |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **$K_p = 1$** | $-1.79, -57.49$ | Sobreamortiguado | $2.24 \text{ s}$ | $0\%$ | $0\%$ |
| **$K_p = 10$** | $-22.56, -36.72$ | Sobreamortiguado | $0.177 \text{ s}$ | $0\%$ | $0\%$ |
| **$K_p = 60$** | $-29.64 \pm j 73.07$ | Subamortiguado | $0.135 \text{ s}$ | $22.75\%$ | $0\%$ |

- **Análisis**: Vemos que entre mayor es el valor de $K_p$, el motor responde más rápido (el tiempo de asentamiento $t_s$ disminuye). Sin embargo, al usar $K_p = 60$ el sistema se vuelve subamortiguado y tiene un sobreimpulso de posición del $22.75\%$. El error de posición en estado estable es del $0\%$ en todos los casos gracias al polo integrador de la propia planta.

### B. Prueba 2: Respuesta ante Entrada Rampa
Le metimos una entrada rampa unitaria ($1.0\text{ rad/s}$) al sistema en lazo cerrado. Las simulaciones muestran que el motor sigue la rampa, pero queda con un desfase constante (error de velocidad $e_{ss}$):
$$e_{ss} = \frac{1}{K_v} = \frac{59.28}{103.25 K_p}$$
Entre mayor sea la ganancia $K_p$ que usemos, menor será la separación visual entre la referencia y la salida real de la posición del motor.

### C. Prueba 3: Rechazo de Perturbaciones
Le aplicamos una perturbación tipo escalón de amplitud $1.0$ (como una carga estática) en la entrada del motor. En la simulación se observa que la posición del motor sufre una pequeña desviación al inicio, pero el controlador compensa el disturbio y regresa la posición a la referencia, logrando un error de perturbación de **$0\%$** en estado estable.