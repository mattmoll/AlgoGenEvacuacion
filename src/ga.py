"""
ga.py — Algoritmo Genético para optimización de planes de evacuación.

Implementa desde cero:
  - Representación: cromosoma entero por posición (vector de índices de ruta)
  - Selección: por torneo o por ruleta
  - Cruce: punto simple o uniforme
  - Mutación: reemplazo puntual por ruta alternativa válida
  - Elitismo: preserva los K mejores entre generaciones
  - Loop evolutivo con registro histórico para graficado
"""

import random as _random
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# INICIALIZACIÓN DE POBLACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def create_individual(sectors, routes, rng=None):
    """
    Crea un individuo aleatorio.

    Cada gen i es un entero en [0, len(routes[sectors[i]]) - 1],
    representando la ruta asignada al sector i.
    """
    if rng is None:
        rng = _random
    return [rng.randint(0, len(routes[s]) - 1) for s in sectors]


def create_population(pop_size, sectors, routes, rng=None):
    """Crea una población inicial de pop_size individuos aleatorios."""
    return [create_individual(sectors, routes, rng) for _ in range(pop_size)]


# ─────────────────────────────────────────────────────────────────────────────
# SELECCIÓN
# ─────────────────────────────────────────────────────────────────────────────

def tournament_selection(population, fitnesses, k=3, rng=None):
    """
    Selección por torneo: elige k individuos al azar y devuelve al mejor.

    Presión selectiva controlable con k (k mayor → más presión).
    """
    if rng is None:
        rng = _random
    indices = rng.choices(range(len(population)), k=k)
    winner = max(indices, key=lambda i: fitnesses[i])
    return population[winner][:]


def roulette_selection(population, fitnesses, rng=None):
    """
    Selección proporcional al fitness (ruleta).

    Favorece exploración cuando los fitness son similares entre sí.
    """
    if rng is None:
        rng = _random
    total = sum(fitnesses)
    if total <= 0:
        return rng.choice(population)[:]
    r = rng.uniform(0, total)
    cumulative = 0.0
    for i, f in enumerate(fitnesses):
        cumulative += f
        if cumulative >= r:
            return population[i][:]
    return population[-1][:]


# ─────────────────────────────────────────────────────────────────────────────
# CRUCE (CROSSOVER)
# ─────────────────────────────────────────────────────────────────────────────

def single_point_crossover(parent1, parent2, rng=None):
    """
    Cruce de un punto: intercambia sufijos a partir de un punto aleatorio.

    Preserva la coherencia del cromosoma porque cada gen es independiente
    (la ruta de un sector no afecta directamente la de otro).
    """
    if rng is None:
        rng = _random
    n = len(parent1)
    if n <= 1:
        return parent1[:], parent2[:]
    point = rng.randint(1, n - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2


def uniform_crossover(parent1, parent2, rng=None):
    """
    Cruce uniforme: cada gen se hereda de uno de los dos padres con p=0.5.

    Mayor exploración que el cruce de un punto; útil cuando el espacio
    de búsqueda es muy discontinuo.
    """
    if rng is None:
        rng = _random
    child1, child2 = [], []
    for g1, g2 in zip(parent1, parent2):
        if rng.random() < 0.5:
            child1.append(g1)
            child2.append(g2)
        else:
            child1.append(g2)
            child2.append(g1)
    return child1, child2


# ─────────────────────────────────────────────────────────────────────────────
# MUTACIÓN
# ─────────────────────────────────────────────────────────────────────────────

def mutate(chromosome, sectors, routes, mutation_rate, rng=None):
    """
    Mutación puntual: con probabilidad mutation_rate, reemplaza la ruta
    del sector i por otra ruta válida elegida al azar para ese sector.

    Garantiza que el cromosoma resultante sea siempre válido (las rutas
    mutadas siguen siendo rutas existentes para su sector).
    """
    if rng is None:
        rng = _random
    mutated = chromosome[:]
    for i, sector in enumerate(sectors):
        if rng.random() < mutation_rate:
            mutated[i] = rng.randint(0, len(routes[sector]) - 1)
    return mutated


# ─────────────────────────────────────────────────────────────────────────────
# LOOP EVOLUTIVO PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

def run_ga(
    sectors,
    routes,
    G,
    simulate_fn,
    fitness_fn,
    pop_size=80,
    n_generations=150,
    mutation_rate=0.10,
    crossover_rate=0.80,
    elitism_k=5,
    selection_method="tournament",
    crossover_method="single_point",
    tournament_k=3,
    seed=42,
    verbose=True,
    run_name="corrida",
):
    """
    Ejecuta el algoritmo genético completo.

    Args:
        sectors:          lista de IDs de sectores
        routes:           dict {sector: [path1, ...]}
        G:                nx.DiGraph del edificio
        simulate_fn:      función(chrom, G, sectors, routes) → (T, D, P)
        fitness_fn:       función(T, D, P) → float
        pop_size:         tamaño de la población
        n_generations:    número de generaciones
        mutation_rate:    probabilidad de mutación por gen
        crossover_rate:   probabilidad de cruce entre dos padres
        elitism_k:        cantidad de élites a preservar directamente
        selection_method: 'tournament' o 'roulette'
        crossover_method: 'single_point' o 'uniform'
        tournament_k:     tamaño del torneo (solo para selection_method='tournament')
        seed:             semilla para reproducibilidad
        verbose:          imprimir progreso cada 20 generaciones
        run_name:         nombre de la corrida para el log

    Returns:
        best_chrom  (list[int]):  mejor cromosoma encontrado
        best_result (tuple):      (T_total, D_max, penalty, fitness) del mejor
        history     (dict):       historial por generación para graficado
    """
    rng = _random.Random(seed)

    # ── Población inicial ──────────────────────────────────────────────────────
    population = create_population(pop_size, sectors, routes, rng)

    def evaluate_all(pop):
        """Evalúa todos los individuos de la población."""
        results = []
        for chrom in pop:
            T, D, P = simulate_fn(chrom, G, sectors, routes)
            f = fitness_fn(T, D, P)
            results.append((T, D, P, f))
        return results

    eval_results = evaluate_all(population)
    fitnesses = [r[3] for r in eval_results]

    best_idx = int(np.argmax(fitnesses))
    best_chrom = population[best_idx][:]
    best_result = eval_results[best_idx]

    # ── Historial ──────────────────────────────────────────────────────────────
    history = {
        "generation":   [],
        "best_fitness": [],
        "mean_fitness": [],
        "best_T_total": [],
        "best_D_max":   [],
        "best_penalty": [],
    }

    def log_gen(gen, b_result, mean_f):
        history["generation"].append(gen)
        history["best_fitness"].append(b_result[3])
        history["mean_fitness"].append(mean_f)
        history["best_T_total"].append(b_result[0])
        history["best_D_max"].append(b_result[1])
        history["best_penalty"].append(b_result[2])

    log_gen(0, best_result, float(np.mean(fitnesses)))

    if verbose:
        T, D, P, f = best_result
        print(f"  [{run_name}] Gen  0 | fitness={f:.6f} | T={T:3d}s | D={D:.0f} | P={P:.0f}")

    # ── Evolución ──────────────────────────────────────────────────────────────
    for gen in range(1, n_generations + 1):

        # Elitismo: los K mejores pasan directamente
        sorted_idx = sorted(range(len(population)), key=lambda i: fitnesses[i], reverse=True)
        new_pop = [population[i][:] for i in sorted_idx[:elitism_k]]

        # Generar hijos hasta completar la nueva población
        while len(new_pop) < pop_size:
            # Selección
            if selection_method == "tournament":
                p1 = tournament_selection(population, fitnesses, k=tournament_k, rng=rng)
                p2 = tournament_selection(population, fitnesses, k=tournament_k, rng=rng)
            else:
                p1 = roulette_selection(population, fitnesses, rng=rng)
                p2 = roulette_selection(population, fitnesses, rng=rng)

            # Cruce
            if rng.random() < crossover_rate:
                if crossover_method == "single_point":
                    c1, c2 = single_point_crossover(p1, p2, rng=rng)
                else:
                    c1, c2 = uniform_crossover(p1, p2, rng=rng)
            else:
                c1, c2 = p1[:], p2[:]

            # Mutación
            c1 = mutate(c1, sectors, routes, mutation_rate, rng=rng)
            c2 = mutate(c2, sectors, routes, mutation_rate, rng=rng)

            new_pop.append(c1)
            if len(new_pop) < pop_size:
                new_pop.append(c2)

        population = new_pop
        eval_results = evaluate_all(population)
        fitnesses = [r[3] for r in eval_results]

        # Actualizar mejor global
        cur_best_idx = int(np.argmax(fitnesses))
        if fitnesses[cur_best_idx] > best_result[3]:
            best_chrom = population[cur_best_idx][:]
            best_result = eval_results[cur_best_idx]

        mean_f = float(np.mean(fitnesses))
        log_gen(gen, best_result, mean_f)

        if verbose and gen % 20 == 0:
            T, D, P, f = best_result
            print(f"  [{run_name}] Gen {gen:3d} | fitness={f:.6f} | T={T:3d}s | D={D:.0f} | P={P:.0f}")

    if verbose:
        T, D, P, f = best_result
        print(f"  [{run_name}] FINAL  | fitness={f:.6f} | T={T:3d}s | D={D:.0f} | P={P:.0f}")

    return best_chrom, best_result, history
