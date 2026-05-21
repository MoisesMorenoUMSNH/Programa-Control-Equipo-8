import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import scipy.signal as signal

def graficar_pz(ceros, polos, estado_sistema, ruta_guardado=None):
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.axvspan(-1000, 0, color='lightgreen', alpha=0.3, label='Estable (SI)')
    ax.axvspan(0, 1000, color='lightcoral', alpha=0.3, label='Inestable (SD)')
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    
    polos_redondeados = [np.round(p, 4) for p in polos]
    ceros_redondeados = [np.round(c, 4) for c in ceros]
    
    conteo_polos = Counter(polos_redondeados)
    conteo_ceros = Counter(ceros_redondeados)

    for p, cantidad in conteo_polos.items():
        ax.scatter(np.real(p), np.imag(p), marker='x', color='red', s=100, linewidth=2, zorder=3)
        if cantidad > 1:
            ax.annotate(f'x{cantidad}', (np.real(p), np.imag(p)), textcoords="offset points", xytext=(8,8), ha='left', color='red', fontweight='bold')
    
    for c, cantidad in conteo_ceros.items():
        ax.scatter(np.real(c), np.imag(c), marker='o', facecolors='none', edgecolors='blue', s=100, linewidth=2, zorder=3)
        if cantidad > 1:
            ax.annotate(f'x{cantidad}', (np.real(c), np.imag(c)), textcoords="offset points", xytext=(8,8), ha='left', color='blue', fontweight='bold')

    ax.scatter([], [], marker='x', color='red', label='Polos')
    ax.scatter([], [], marker='o', facecolors='none', edgecolors='blue', label='Ceros')

    todos_los_puntos = np.concatenate((polos, ceros, [0])) if len(polos) > 0 or len(ceros) > 0 else np.array([0])
    max_val = max(np.max(np.abs(np.real(todos_los_puntos))), np.max(np.abs(np.imag(todos_los_puntos))))
    limite = max_val * 1.5 if max_val > 0 else 5
    
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    
    plt.title(f'Mapa de Polos y Ceros\nSistema: {estado_sistema}', fontsize=12, fontweight='bold')
    plt.xlabel('Eje Real (Re)')
    plt.ylabel('Eje Imaginario (Im)')
    plt.legend(loc='upper right')
    plt.grid(True, linestyle='--', alpha=0.7)
    if ruta_guardado:
        plt.savefig(ruta_guardado)
        
    plt.show(block=False)

def graficar_escalon(num_abierto, den_abierto, num_cerrado, den_cerrado, amplitud, ruta_lazos=None):
    # Creamos los sistemas
    sys_la = signal.TransferFunction(num_abierto, den_abierto)
    sys_lc = signal.TransferFunction(num_cerrado, den_cerrado)
    
    # Calculamos con más puntos para precisión en el transitorio
    t_la, y_la = signal.step(sys_la, N=2000)
    t_lc, y_lc = signal.step(sys_lc, T=t_la)

    y_la = y_la * amplitud
    y_lc = y_lc * amplitud

    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Graficamos ambas curvas con el mismo eje de tiempo
    ax.plot(t_la, y_la, color='blue', label='Lazo Abierto', linewidth=1.5)
    ax.plot(t_lc, y_lc, color='orange', label='Lazo Cerrado', linewidth=1.5)
    
    # Función auxiliar para marcar los picos (sobreimpulso máximo)
    def marcar_pico(t, y, color_marcador):
        if len(y) == 0: return
        vf = y[-1]
        pico_max = np.max(y)
        # Si hay sobreimpulso
        if pico_max > vf and vf > 1e-9:
            idx_pico = np.argmax(y)
            ax.plot(t[idx_pico], y[idx_pico], marker='o', markersize=6, color=color_marcador)
            ax.annotate(f'Pico: {y[idx_pico]:.2f}', 
                        xy=(t[idx_pico], y[idx_pico]), 
                        xytext=(5, 5), textcoords='offset points', 
                        color=color_marcador, fontsize=9, fontweight='bold')

    marcar_pico(t_la, y_la, 'darkblue')
    marcar_pico(t_lc, y_lc, 'darkred')

    # Líneas de valor final (estado estable)
    if abs(y_la[-1]) > 1e-9 and y_la[-1] < 1e6:
        ax.axhline(y_la[-1], color='blue', linestyle=':', alpha=0.5)
    if abs(y_lc[-1]) > 1e-9 and y_lc[-1] < 1e6:
        ax.axhline(y_lc[-1], color='orange', linestyle=':', alpha=0.5)
    
    ax.axhline(0, color='black', linestyle='-', alpha=0.3)
    ax.set_title(f'Respuesta Transitoria al Escalón (Amplitud = {amplitud})', fontsize=12)
    ax.set_xlabel('Tiempo (s)')
    ax.set_ylabel('Amplitud')
    ax.legend(loc='upper right')
    ax.grid(True, linestyle='--', alpha=0.5)
    
    plt.tight_layout()
    if ruta_lazos:
        plt.savefig(ruta_lazos)
        
    plt.show(block=False)