# Control de Posición de un Motor de CD con Tren de Engranes
**Proyecto de Control Analógico I — Equipo 8**

Este programa es una herramienta interactiva en Python para simular, analizar y sintonizar el sistema de control de posición de nuestro motor de CD, comparando el comportamiento en Lazo Abierto y Lazo Cerrado ante distintas entradas (escalón, rampa y tren de pulsos).

---

## 👥 Integrantes (Equipo 8)
* **Moisés Moreno Cortez**
* **Kassandra Delgado Mendez**
* **Luz Selena**
* **Luis Mendoza**

*Facultad de Ingeniería Eléctrica — Ingeniería en Computación*

---

## 🛠️ Requisitos de Instalación
Asegúrate de tener instaladas las librerías necesarias ejecutando en tu terminal:
```bash
pip install numpy scipy matplotlib sympy
```

---

## 🚀 ¿Cómo ejecutar el programa?
Para iniciar la herramienta interactiva, corre el siguiente comando en la carpeta raíz del proyecto:
```bash
python3 main.py
```

El programa te guiará paso a paso en la consola para elegir las señales de entrada, definir las ganancias del controlador ($K_p$, $K_i$), configurar la retroalimentación ($H$), e ingresar las funciones de transferencia para ver los gráficos en tiempo real y guardar los reportes automáticos en la carpeta `Resultados/`.