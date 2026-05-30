"""
main.py — Punto de entrada: ejecuta las 5 corridas del TP2.

Cada corrida varía al menos un parámetro del AG (requerimiento del enunciado):
  Corrida 1 — Baseline:            torneo, cruce punto único, mutación 10%
  Corrida 2 — Alta mutación:        igual que 1 pero mutación 30%
  Corrida 3 — Selección ruleta:     igual que 1 pero selección por ruleta
  Corrida 4 — Prioridad densidad:   W2=2.0 (penaliza más los cuellos de botella)
  Corrida 5 — Emergencia:           escalera A bloqueada, pop mayor, cruce uniforme

Salidas generadas en results/:
  - building_layout.png
  - corrida_0X_<nombre>_fitness.png   (gráfico requerido)
  - corrida_0X_<nombre>_history.csv   (log requerido)
  - resumen_corridas.csv
"""

import os
import sys

# Forzar UTF-8 en la consola de Windows para evitar errores con tildes y símbolos
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Permitir importar src/ desde cualquier directorio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.building   import build_utn_graph, precompute_routes, get_sectors, building_summary
from src.simulation import simulate_evacuation, compute_fitness
from src.ga         import run_ga
from src.visualization import (
    plot_fitness_evolution,
    plot_building_layout,
    save_run_csv,
    save_summary_csv,
    print_best_solution,
)

os.makedirs("results", exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN DE CORRIDAS
# ─────────────────────────────────────────────────────────────────────────────

RUNS = [
    {
        "name":             "corrida_01_baseline",
        "desc":             "Baseline: torneo k=3, cruce punto único, mutación 10%",
        "pop_size":         80,
        "n_generations":    150,
        "mutation_rate":    0.10,
        "crossover_rate":   0.80,
        "elitism_k":        5,
        "selection_method": "tournament",
        "crossover_method": "single_point",
        "tournament_k":     3,
        "W1": 1.0, "W2": 0.5, "W3": 10.0,
        "seed":             42,
        "blocked_edges":    None,
    },
    {
        "name":             "corrida_02_alta_mutacion",
        "desc":             "Alta mutación (30%): mayor exploración, posible menor convergencia",
        "pop_size":         80,
        "n_generations":    150,
        "mutation_rate":    0.30,
        "crossover_rate":   0.80,
        "elitism_k":        5,
        "selection_method": "tournament",
        "crossover_method": "single_point",
        "tournament_k":     3,
        "W1": 1.0, "W2": 0.5, "W3": 10.0,
        "seed":             42,
        "blocked_edges":    None,
    },
    {
        "name":             "corrida_03_ruleta",
        "desc":             "Selección por ruleta: menor presión selectiva que torneo",
        "pop_size":         80,
        "n_generations":    150,
        "mutation_rate":    0.10,
        "crossover_rate":   0.80,
        "elitism_k":        5,
        "selection_method": "roulette",
        "crossover_method": "single_point",
        "tournament_k":     3,
        "W1": 1.0, "W2": 0.5, "W3": 10.0,
        "seed":             42,
        "blocked_edges":    None,
    },
    {
        "name":             "corrida_04_prioridad_densidad",
        "desc":             "W2=2.0: penaliza el doble los cuellos de botella vs. tiempo",
        "pop_size":         80,
        "n_generations":    150,
        "mutation_rate":    0.10,
        "crossover_rate":   0.80,
        "elitism_k":        5,
        "selection_method": "tournament",
        "crossover_method": "single_point",
        "tournament_k":     3,
        "W1": 0.5, "W2": 2.0, "W3": 10.0,
        "seed":             42,
        "blocked_edges":    None,
    },
    {
        "name":             "corrida_05_emergencia_escalera_bloqueada",
        "desc":             "Escalera A bloqueada (incendio): pop=100, cruce uniforme, mut=15%",
        "pop_size":         100,
        "n_generations":    200,
        "mutation_rate":    0.15,
        "crossover_rate":   0.80,
        "elitism_k":        5,
        "selection_method": "tournament",
        "crossover_method": "uniform",
        "tournament_k":     3,
        "W1": 1.0, "W2": 0.5, "W3": 10.0,
        "seed":             42,
        # Bloquea la escalera A completa (simula un incendio en la caja de escaleras)
        "blocked_edges":    [
            ("STAIR_A_6F", "STAIR_A_5F"),
            ("STAIR_A_5F", "STAIR_A_4F"),
            ("STAIR_A_4F", "STAIR_A_3F"),
            ("STAIR_A_3F", "STAIR_A_2F"),
            ("STAIR_A_2F", "STAIR_A_1F"),
            ("STAIR_A_1F", "STAIR_A_GF"),
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# CONSTRUCCIÓN DEL EDIFICIO BASE
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("  ALGORITMO GENETICO - OPTIMIZACION DE EVACUACION UTN")
print("  TP2 Sistemas Inteligentes - Grupo 6 - 2026")
print("=" * 65)

print("\nConstruyendo grafo del edificio...")
G_base = build_utn_graph()
routes_base = precompute_routes(G_base)
sectors_base = get_sectors(G_base)
building_summary(G_base, routes_base)

print("\nGenerando plano del edificio...")
plot_building_layout(G_base, save_path="results/building_layout.png")


# ─────────────────────────────────────────────────────────────────────────────
# EJECUCIÓN DE CORRIDAS
# ─────────────────────────────────────────────────────────────────────────────

all_results = []

for run_cfg in RUNS:
    print(f"\n{'─' * 65}")
    print(f"  {run_cfg['name']}")
    print(f"  {run_cfg['desc']}")
    print(f"{'─' * 65}")

    # Reconstruir grafo con posibles bloqueos
    G_run = build_utn_graph(blocked_edges=run_cfg.get("blocked_edges"))
    routes_run = precompute_routes(G_run)
    sectors_run = get_sectors(G_run)

    W1 = run_cfg["W1"]
    W2 = run_cfg["W2"]
    W3 = run_cfg["W3"]

    # Funciones de simulación y fitness con los pesos de esta corrida
    # (uso de valores por defecto para evitar el problema del closure en loops)
    def make_fitness_fn(w1, w2, w3):
        def fit_fn(T, D, P):
            return compute_fitness(T, D, P, W1=w1, W2=w2, W3=w3)
        return fit_fn

    fit_fn = make_fitness_fn(W1, W2, W3)

    best_chrom, best_result, history = run_ga(
        sectors         = sectors_run,
        routes          = routes_run,
        G               = G_run,
        simulate_fn     = simulate_evacuation,
        fitness_fn      = fit_fn,
        pop_size        = run_cfg["pop_size"],
        n_generations   = run_cfg["n_generations"],
        mutation_rate   = run_cfg["mutation_rate"],
        crossover_rate  = run_cfg["crossover_rate"],
        elitism_k       = run_cfg["elitism_k"],
        selection_method= run_cfg["selection_method"],
        crossover_method= run_cfg["crossover_method"],
        tournament_k    = run_cfg["tournament_k"],
        seed            = run_cfg["seed"],
        verbose         = True,
        run_name        = run_cfg["name"],
    )

    # Imprimir mejor solución
    print_best_solution(best_chrom, best_result, sectors_run, routes_run, G_run,
                        run_name=run_cfg["name"])

    # Guardar gráfico de fitness (requerido por el enunciado)
    plot_fitness_evolution(
        history,
        run_name = run_cfg["name"],
        run_desc = run_cfg["desc"],
        save_path = f"results/{run_cfg['name']}_fitness.png",
    )

    # Guardar log CSV (requerido por el enunciado)
    cfg_to_log = {k: v for k, v in run_cfg.items() if k not in ("blocked_edges",)}
    save_run_csv(history, cfg_to_log, run_cfg["name"], save_dir="results")

    T, D, P, fitness = best_result
    all_results.append({
        "corrida":          run_cfg["name"],
        "descripcion":      run_cfg["desc"],
        "pop_size":         run_cfg["pop_size"],
        "n_generations":    run_cfg["n_generations"],
        "mutation_rate":    run_cfg["mutation_rate"],
        "selection":        run_cfg["selection_method"],
        "crossover":        run_cfg["crossover_method"],
        "W1": W1, "W2": W2, "W3": W3,
        "T_total_s":        T,
        "T_total_min":      round(T / 60, 2),
        "D_max":            round(D, 1),
        "penalty":          round(P, 1),
        "best_fitness":     round(fitness, 8),
        "emergencia":       run_cfg.get("blocked_edges") is not None,
    })


# ─────────────────────────────────────────────────────────────────────────────
# RESUMEN COMPARATIVO
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 65)
print("  RESUMEN COMPARATIVO DE TODAS LAS CORRIDAS")
print("=" * 65)

import pandas as pd
df = pd.DataFrame(all_results)
cols_display = ["corrida", "T_total_s", "T_total_min", "D_max", "penalty", "best_fitness"]
print(df[cols_display].to_string(index=False))

save_summary_csv(all_results, save_dir="results")

print("\n¡Todas las corridas completadas! Resultados en la carpeta results/")
