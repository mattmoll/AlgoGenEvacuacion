"""
visualization.py — Graficado y logging de resultados.

Genera:
  - Gráfico de evolución del fitness (obligatorio por el enunciado)
  - Plano del edificio como grafo
  - Logs CSV de cada corrida (obligatorio por el enunciado)
  - Informe de la mejor solución encontrada
"""

import os
import math
import matplotlib
matplotlib.use("Agg")   # backend sin pantalla (funciona en cualquier entorno)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO DE EVOLUCIÓN DEL FITNESS
# ─────────────────────────────────────────────────────────────────────────────

def plot_fitness_evolution(history, run_name, run_desc="", save_path=None):
    """
    Genera un panel 2×2 con la evolución del fitness y las métricas clave.

    Paneles:
      [0,0] Fitness: mejor y promedio por generación
      [0,1] T_total: tiempo de evacuación del mejor
      [1,0] D_max:   densidad máxima en nodos
      [1,1] Penalty: penalización acumulada
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"Evolución del AG — {run_name}\n{run_desc}",
        fontsize=13, fontweight="bold"
    )

    gens = history["generation"]

    # ── Fitness ───────────────────────────────────────────────────────────────
    ax = axes[0, 0]
    ax.plot(gens, history["best_fitness"],  "b-",  lw=2,   label="Mejor fitness")
    ax.plot(gens, history["mean_fitness"],  "r--", lw=1.2, alpha=0.7, label="Fitness promedio")
    ax.set_xlabel("Generación")
    ax.set_ylabel("Fitness")
    ax.set_title("Evolución del Fitness")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # ── T_total ───────────────────────────────────────────────────────────────
    ax = axes[0, 1]
    ax.plot(gens, history["best_T_total"], "g-", lw=2)
    ax.set_xlabel("Generación")
    ax.set_ylabel("Tiempo (s)")
    ax.set_title("Makespan — Tiempo de Evacuación Total")
    ax.grid(True, alpha=0.3)

    # ── D_max ─────────────────────────────────────────────────────────────────
    ax = axes[1, 0]
    ax.plot(gens, history["best_D_max"], "m-", lw=2)
    ax.set_xlabel("Generación")
    ax.set_ylabel("Personas en nodo")
    ax.set_title("Densidad Máxima en Nodos (cuellos de botella)")
    ax.grid(True, alpha=0.3)

    # ── Penalización ──────────────────────────────────────────────────────────
    ax = axes[1, 1]
    ax.plot(gens, history["best_penalty"], "r-", lw=2)
    ax.set_xlabel("Generación")
    ax.set_ylabel("Penalización")
    ax.set_title("Penalización (rutas inválidas / personas no evacuadas)")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Grafico guardado -> {save_path}")

    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# PLANO DEL EDIFICIO
# ─────────────────────────────────────────────────────────────────────────────

def plot_building_layout(G, save_path=None):
    """
    Visualiza el grafo del edificio con colores por tipo de nodo y piso.

    Disposición:
      - Eje Y = piso (0=PB, 1=1P, 2=2P)
      - Eje X = posición lateral (distribución automática)
    """
    # Posicionamiento por piso (detecta automaticamente los pisos presentes)
    all_floors = sorted(set(data.get("floor", 0) for _, data in G.nodes(data=True)))
    floor_nodes = {f: [] for f in all_floors}
    for node, data in G.nodes(data=True):
        floor_nodes[data.get("floor", 0)].append(node)

    pos = {}
    for floor, nodes in floor_nodes.items():
        nodes_sorted = sorted(nodes)
        n = len(nodes_sorted)
        for i, node in enumerate(nodes_sorted):
            pos[node] = ((i - n / 2) * 3.0, floor * 4.0)

    # Colores por tipo de nodo
    colors = []
    for node, data in G.nodes(data=True):
        if data.get("is_exit"):
            colors.append("#2ecc71")       # verde: salida
        elif data.get("is_sector"):
            colors.append("#3498db")       # azul: aula/sector
        else:
            colors.append("#bdc3c7")       # gris: pasillo/escalera

    labels = {n: d.get("label", n) for n, d in G.nodes(data=True)}

    fig, ax = plt.subplots(figsize=(22, 16))

    nx.draw_networkx(
        G, pos, labels=labels,
        node_color=colors, node_size=1400,
        font_size=6.5, font_weight="bold",
        arrows=True, arrowsize=12,
        edge_color="#95a5a6", alpha=0.85,
        ax=ax,
        connectionstyle="arc3,rad=0.08",
    )

    # Etiquetas de piso
    floor_label_map = {
        0: "Planta Baja", 1: "Primer Piso",  2: "Segundo Piso",
        3: "Tercer Piso", 4: "Cuarto Piso",  5: "Quinto Piso",
    }
    for floor in all_floors:
        label = floor_label_map.get(floor, f"Piso {floor}")
        ax.text(-8.5, floor * 4.0, label, fontsize=10, va="center",
                fontweight="bold", color="#2c3e50",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#ecf0f1", alpha=0.8))

    # Leyenda
    legend_elements = [
        mpatches.Patch(facecolor="#2ecc71", label="Salida"),
        mpatches.Patch(facecolor="#3498db", label="Sector / Aula"),
        mpatches.Patch(facecolor="#bdc3c7", label="Pasillo / Escalera"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=10)
    ax.set_title("Plano del Edificio UTN — Grafo de Evacuación", fontsize=14, fontweight="bold")
    ax.axis("off")

    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"  Plano guardado -> {save_path}")
    plt.close(fig)


# ─────────────────────────────────────────────────────────────────────────────
# LOGGING EN CSV
# ─────────────────────────────────────────────────────────────────────────────

def save_run_csv(history, run_config, run_name, save_dir="results"):
    """
    Guarda el historial de la corrida en un CSV con todos los parámetros.

    Columnas:
        run_name, generation, best_fitness, mean_fitness,
        best_T_total, best_D_max, best_penalty, <parámetros de configuración>
    """
    os.makedirs(save_dir, exist_ok=True)

    df = pd.DataFrame(history)
    df.insert(0, "run_name", run_name)

    # Añadir parámetros de configuración como columnas (para comparación)
    for key, val in run_config.items():
        df[key] = str(val)

    csv_path = os.path.join(save_dir, f"{run_name}_history.csv")
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"  Log CSV guardado -> {csv_path}")
    return csv_path


def save_summary_csv(all_results, save_dir="results"):
    """Guarda un CSV comparativo con los resultados finales de todas las corridas."""
    os.makedirs(save_dir, exist_ok=True)
    df = pd.DataFrame(all_results)
    path = os.path.join(save_dir, "resumen_corridas.csv")
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"\nResumen comparativo guardado -> {path}")
    return path


# ─────────────────────────────────────────────────────────────────────────────
# INFORME DE LA MEJOR SOLUCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def print_best_solution(best_chrom, best_result, sectors, routes, G, run_name=""):
    """
    Imprime un informe legible del mejor plan de evacuación encontrado.
    Muestra, para cada sector, la ruta asignada, la salida objetivo y
    el tiempo de viaje estimado.
    """
    T, D, P, fitness = best_result

    print()
    print("=" * 65)
    print(f"  MEJOR SOLUCIÓN — {run_name}")
    print("=" * 65)
    print(f"  Fitness              : {fitness:.8f}")
    print(f"  Tiempo evacuación    : {T} s  ({T / 60:.1f} min)")
    print(f"  Densidad máxima      : {D:.0f} personas en un nodo")
    print(f"  Penalización         : {P:.1f}")
    total_pop = sum(G.nodes[s]["population"] for s in sectors)
    print(f"  Población total      : {total_pop} personas")
    print()
    print(f"  {'Sector':<24} {'Pop':>4}  {'Salida':<24}  {'Ruta':>5}  {'tt':>4}")
    print("  " + "-" * 63)

    for i, sector in enumerate(sectors):
        ridx = best_chrom[i] % len(routes[sector])
        route = routes[sector][ridx]
        pop = G.nodes[sector]["population"]
        lbl = G.nodes[sector]["label"]
        exit_node = route[-1]
        exit_lbl = G.nodes[exit_node]["label"]
        tt = sum(G[route[j]][route[j + 1]]["travel_time"] for j in range(len(route) - 1))
        route_str = "->".join(r.replace("S_", "").replace("CORR_", "C").replace("STAIR_", "SC")
                               .replace("HALL_GF", "Hall").replace("EXIT_", "E") for r in route)
        print(f"  {lbl:<24} {pop:>4}  {exit_lbl:<24}  {len(route):>5}  {tt:>3}s")

    print("=" * 65)
