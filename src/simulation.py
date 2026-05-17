"""
simulation.py — Simulación discreta de flujo de evacuación.

Modelo de tiempo discreto (1 paso = 1 segundo):
  - Cada arista tiene capacidad (personas/s) y tiempo de recorrido (s).
  - Las personas se agrupan por (sector_origen, índice_ruta).
  - En cada paso se mueven tantas personas como permite la capacidad
    disponible en la arista, de forma proporcional si hay competencia.
  - La función de fitness implementa la fórmula de la propuesta aprobada:
        Fitness = 1 / (W1·T_total + W2·D_max + W3·P)
"""

import heapq
from collections import defaultdict


def simulate_evacuation(chromosome, G, sectors, routes, max_time=400):
    """
    Simula la evacuación completa del edificio dado un cromosoma.

    Un cromosoma es una lista de enteros [r0, r1, ..., r_{N-1}] donde
    chromosome[i] es el índice de la ruta asignada al sector sectors[i].

    La simulación usa una heap de eventos (transit_heap) para registrar
    cuándo llega cada grupo a su próximo nodo.

    Args:
        chromosome: list[int], longitud == len(sectors)
        G:          nx.DiGraph del edificio
        sectors:    list[str], IDs de los sectores (mismo orden que el cromosoma)
        routes:     dict {sector_id: [path1, path2, ...]}
        max_time:   int, límite de pasos de simulación (segundos)

    Returns:
        T_total (int):   paso en que evacuó la última persona (≤ max_time)
        D_max   (float): máxima cantidad de personas simultáneas en cualquier nodo
        penalty (float): 0 si todos evacuaron, >0 si hubo problemas
    """
    # ── 1. Inicialización ──────────────────────────────────────────────────────
    # queues[node][(sector, route_idx)] = cantidad de personas esperando en node
    queues = defaultdict(lambda: defaultdict(int))
    penalty = 0.0

    for i, sector in enumerate(sectors):
        sector_routes = routes.get(sector, [])
        if not sector_routes:
            penalty += G.nodes[sector]["population"] * 100.0
            continue
        ridx = chromosome[i] % len(sector_routes)
        pop = G.nodes[sector]["population"]
        queues[sector][(sector, ridx)] += pop

    # ── 2. Precómputo de "próximo salto" por (sector, ridx, nodo_actual) ──────
    # next_hop[(sector, ridx, node)] = próximo_nodo_en_la_ruta
    next_hop = {}
    for sector in sectors:
        for ridx, path in enumerate(routes.get(sector, [])):
            for j in range(len(path) - 1):
                next_hop[(sector, ridx, path[j])] = path[j + 1]

    # ── 3. Variables de seguimiento ───────────────────────────────────────────
    exits = {n for n, d in G.nodes(data=True) if d.get("is_exit")}
    total_pop = sum(G.nodes[s]["population"] for s in sectors)
    evacuated = 0
    D_max = 0.0
    T_total = max_time

    # Heap de tránsito: (arrival_time, dest_node, sector, ridx, count)
    transit_heap = []

    # ── 4. Bucle de simulación ────────────────────────────────────────────────
    for t in range(max_time):

        # 4a. Procesar llegadas al paso t
        while transit_heap and transit_heap[0][0] <= t:
            arr_t, dest, sec, ridx, count = heapq.heappop(transit_heap)
            if dest in exits:
                evacuated += count
            else:
                queues[dest][(sec, ridx)] += count

        # Condición de parada anticipada
        if evacuated >= total_pop:
            T_total = t
            break

        # 4b. Actualizar densidad máxima
        for node, groups in queues.items():
            total_here = sum(v for v in groups.values() if v > 0)
            if total_here > D_max:
                D_max = total_here

        # 4c. Planificar movimientos: agrupar demanda por arista
        # edge_demand[(u, v)] = list of (sector, ridx, count, from_node)
        edge_demand = defaultdict(list)

        for node, groups in queues.items():
            for (sec, ridx), count in list(groups.items()):
                if count <= 0:
                    continue
                next_node = next_hop.get((sec, ridx, node))
                if next_node is None:
                    continue
                if G.has_edge(node, next_node):
                    edge_demand[(node, next_node)].append((sec, ridx, count, node))
                else:
                    # Arista bloqueada → penalización
                    penalty += count * 50.0
                    queues[node][(sec, ridx)] = 0

        # 4d. Ejecutar movimientos respetando la capacidad de cada arista
        for (u, v), demands in edge_demand.items():
            cap = G[u][v]["capacity"]
            tt = G[u][v]["travel_time"]
            total_demand = sum(d[2] for d in demands)

            if total_demand == 0:
                continue

            # Fracción de la demanda que puede moverse este paso
            ratio = min(1.0, cap / total_demand)

            for sec, ridx, count, node in demands:
                if ratio < 1.0:
                    # Movimiento proporcional (al menos 1 si hay alguno)
                    moving = max(1, int(count * ratio))
                    moving = min(moving, queues[node].get((sec, ridx), 0))
                else:
                    moving = count

                if moving <= 0:
                    continue

                queues[node][(sec, ridx)] -= moving
                heapq.heappush(transit_heap, (t + tt, v, sec, ridx, moving))

    else:
        # No todos evacuaron dentro del tiempo límite
        remaining = total_pop - evacuated
        penalty += remaining * 200.0

    return T_total, D_max, penalty


def compute_fitness(T_total, D_max, penalty, W1=1.0, W2=0.5, W3=10.0):
    """
    Función de aptitud (maximizar): inverso del costo ponderado.

        Fitness = 1 / (W1·T_total + W2·D_max + W3·penalty + ε)

    Valores más altos indican mejores planes de evacuación.

    Args:
        T_total: tiempo de evacuación del último individuo (makespan)
        D_max:   densidad máxima en cualquier nodo durante la simulación
        penalty: penalización por rutas inválidas o personas no evacuadas
        W1, W2, W3: pesos definidos por el usuario

    Returns:
        float: valor de fitness (siempre > 0)
    """
    cost = W1 * T_total + W2 * D_max + W3 * penalty
    return 1.0 / (cost + 1e-6)
