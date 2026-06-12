# Gráficas de sistemas de control
# Equipo 8 - Control Analogico I - CONTROL DE POSICION DE UN MOTOR DE CD CON TREN DE ENGRANES

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter

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

def graficar_respuesta(t_la, y_la, t_lc, y_lc, tipo_entrada, amplitud,
                       t_dist=None, y_dist=None, amp_dist=1.0,
                       tipo_control=None, kp=None, ki=None, H=1.0,
                       y_ref=None, ts_la=None, ts_lc=None, ruta_guardado=None):
    tiene_perturbacion = t_dist is not None and y_dist is not None
    if tiene_perturbacion:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    else:
        fig, ax1 = plt.subplots(figsize=(8, 6))
        ax2 = None
        
    # --- SUBPLOT 1: RESPUESTA A LA ENTRADA ---
    ax1.plot(t_la, y_la, color='blue', label='Lazo Abierto', linewidth=1.5)
    
    etiqueta_lc = 'Lazo Cerrado'
    if tipo_control is not None and kp is not None:
        params_str = f'Kp={kp}'
        if tipo_control == 'PI' and ki is not None:
            params_str += f', Ki={ki}'
        if H != 1.0:
            params_str += f', H={H}'
        etiqueta_lc += f' ({tipo_control}: {params_str})'
            
    ax1.plot(t_lc, y_lc, color='orange', label=etiqueta_lc, linewidth=1.5)
    
    # Dibujar la entrada ideal
    if y_ref is not None:
        ax1.plot(t_lc, y_ref, color='gray', linestyle='--', label='Referencia Ideal', alpha=0.7)
    elif tipo_entrada.upper() == 'RAMPA':
        ax1.plot(t_lc, amplitud * t_lc, color='gray', linestyle='--', label=f'Rampa Ideal (A={amplitud})', alpha=0.7)
    else:
        ax1.axhline(amplitud, color='gray', linestyle='--', label=f'Escalón Ideal (A={amplitud})', alpha=0.7)
        
    # Marcar los picos de sobreimpulso máximo (solo para escalón)
    if tipo_entrada.upper() == 'ESCALÓN':
        _marcar_pico(ax1, t_la, y_la, 'darkblue')
        _marcar_pico(ax1, t_lc, y_lc, 'darkred')
        
        # Líneas de estado estable
        if abs(y_la[-1]) > 1e-9 and y_la[-1] < 1e6:
            ax1.axhline(y_la[-1], color='blue', linestyle=':', alpha=0.5)
        if abs(y_lc[-1]) > 1e-9 and y_lc[-1] < 1e6:
            ax1.axhline(y_lc[-1], color='orange', linestyle=':', alpha=0.5)

    # Dibujar líneas verticales de tiempo de estabilización ts (criterio del 2%)
    if ts_la is not None and np.isfinite(ts_la) and ts_la > 0 and ts_la < t_la[-1]:
        ax1.axvline(ts_la, color='blue', linestyle=':', alpha=0.7, label=f'ts Lazo Abierto ({ts_la:.3g}s)')
    if ts_lc is not None and np.isfinite(ts_lc) and ts_lc > 0 and ts_lc < t_lc[-1]:
        ax1.axvline(ts_lc, color='orange', linestyle=':', alpha=0.7, label=f'ts Lazo Cerrado ({ts_lc:.3g}s)')

    ax1.axhline(0, color='black', linestyle='-', alpha=0.3)

    titulo_resp = f'Respuesta a la entrada: {tipo_entrada} (Amplitud = {amplitud})'
    if tipo_control is not None and kp is not None:
        params_str = f'Kp = {kp}'
        if tipo_control == 'PI' and ki is not None:
            params_str += f', Ki = {ki}'
        if H != 1.0:
            params_str += f', H = {H}'
        titulo_resp += f'\nControlador {tipo_control} ({params_str})'

    ax1.set_title(titulo_resp, fontsize=11, fontweight='bold')
    ax1.set_xlabel('Tiempo (s)')
    ax1.set_ylabel('Amplitud')
    ax1.legend(loc='upper left' if tipo_entrada.upper() == 'RAMPA' else 'lower right')
    ax1.grid(True, linestyle='--', alpha=0.5)

    # --- SUBPLOT 2: RESPUESTA A LA PERTURBACIÓN (si aplica) ---
    if ax2 is not None:
        ax2.plot(t_dist, y_dist, color='red', label='Respuesta a Perturbación', linewidth=1.5)
        ax2.axhline(0, color='black', linestyle='-', alpha=0.3)
        if len(y_dist) > 0:
            vf_d = y_dist[-1]
            ax2.axhline(vf_d, color='darkred', linestyle=':', alpha=0.5, label=f'Error final = {vf_d:.3g}')
            
        ax2.set_title(f'Rechazo a Perturbación (Escalón A = {amp_dist})', fontsize=11, fontweight='bold')
        ax2.set_xlabel('Tiempo (s)')
        ax2.set_ylabel('Amplitud de Salida')
        ax2.legend(loc='upper right')
        ax2.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    if ruta_guardado:
        plt.savefig(ruta_guardado)
        
    plt.show()

def _marcar_pico(ax, t, y, color_marcador):
    if len(y) == 0:
        return
    vf = y[-1]
    pico_max = np.max(y)
    if pico_max > vf and vf > 1e-9:
        idx_pico = np.argmax(y)
        ax.plot(t[idx_pico], y[idx_pico], marker='o', markersize=6, color=color_marcador)
        ax.annotate(f'Pico: {y[idx_pico]:.2f}', 
                    xy=(t[idx_pico], y[idx_pico]), 
                    xytext=(5, 5), textcoords='offset points', 
                    color=color_marcador, fontsize=9, fontweight='bold')