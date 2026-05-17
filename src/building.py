"""
building.py — Modelado del edificio como grafo dirigido (NetworkX).

Representa la sede UTN (fictional) con:
  - Nodos: sectores/aulas, pasillos, escaleras, salidas
  - Aristas dirigidas en dirección de evacuación (hacia las salidas)
  - Atributos de arista: capacity (personas/s) y travel_time (segundos)
  - Atributos de nodo: population, is_exit, is_sector, label, floor
"""

import networkx as nx
from itertools import islice


def build_utn_graph(blocked_edges=None):
    """
    Construye el grafo dirigido del edificio UTN (3 pisos, 12 sectores, 3 salidas).

    Planta Baja (floor=0):  4 aulas/labs → corredores → hall → EXIT_A / EXIT_B
    Primer Piso (floor=1):  4 aulas      → corredores → escaleras → PB → salidas
    Segundo Piso (floor=2): 4 aulas      → corredores → escaleras → 1P → PB → salidas
                            También puede usar EXIT_C (salida de emergencia en 2P)

    Args:
        blocked_edges: lista de tuplas (u, v) a eliminar del grafo (simula obstáculos).

    Returns:
        G: nx.DiGraph con el edificio modelado.
    """
    G = nx.DiGraph()

    # ── SALIDAS ───────────────────────────────────────────────────────────────
    G.add_node("EXIT_A",
               population=0, is_exit=True, is_sector=False,
               label="Salida Principal", floor=0)
    G.add_node("EXIT_B",
               population=0, is_exit=True, is_sector=False,
               label="Salida Lateral", floor=0)
    G.add_node("EXIT_C",
               population=0, is_exit=True, is_sector=False,
               label="Salida Emergencia 2P", floor=2)

    # ── PLANTA BAJA ───────────────────────────────────────────────────────────
    G.add_node("HALL_GF",    population=0, is_exit=False, is_sector=False, label="Hall PB",            floor=0)
    G.add_node("CORR_GF_E",  population=0, is_exit=False, is_sector=False, label="Corredor PB Este",   floor=0)
    G.add_node("CORR_GF_W",  population=0, is_exit=False, is_sector=False, label="Corredor PB Oeste",  floor=0)
    G.add_node("STAIR_A_GF", population=0, is_exit=False, is_sector=False, label="Escalera A (PB)",    floor=0)
    G.add_node("STAIR_B_GF", population=0, is_exit=False, is_sector=False, label="Escalera B (PB)",    floor=0)

    G.add_node("S_AULA_001", population=35, is_exit=False, is_sector=True, label="Aula 001",           floor=0)
    G.add_node("S_AULA_002", population=30, is_exit=False, is_sector=True, label="Aula 002",           floor=0)
    G.add_node("S_LAB_COMP", population=28, is_exit=False, is_sector=True, label="Lab. Computación",   floor=0)
    G.add_node("S_BIBLIO",   population=20, is_exit=False, is_sector=True, label="Biblioteca",         floor=0)

    # ── PRIMER PISO ───────────────────────────────────────────────────────────
    G.add_node("CORR_1F_E",  population=0, is_exit=False, is_sector=False, label="Corredor 1P Este",   floor=1)
    G.add_node("CORR_1F_W",  population=0, is_exit=False, is_sector=False, label="Corredor 1P Oeste",  floor=1)
    G.add_node("STAIR_A_1F", population=0, is_exit=False, is_sector=False, label="Escalera A (1P)",    floor=1)
    G.add_node("STAIR_B_1F", population=0, is_exit=False, is_sector=False, label="Escalera B (1P)",    floor=1)

    G.add_node("S_AULA_101",   population=42, is_exit=False, is_sector=True, label="Aula 101",         floor=1)
    G.add_node("S_AULA_102",   population=40, is_exit=False, is_sector=True, label="Aula 102",         floor=1)
    G.add_node("S_AULA_103",   population=38, is_exit=False, is_sector=True, label="Aula 103",         floor=1)
    G.add_node("S_SALA_PROF",  population=12, is_exit=False, is_sector=True, label="Sala Profesores",  floor=1)

    # ── SEGUNDO PISO ──────────────────────────────────────────────────────────
    G.add_node("CORR_2F_E",  population=0, is_exit=False, is_sector=False, label="Corredor 2P Este",   floor=2)
    G.add_node("CORR_2F_W",  population=0, is_exit=False, is_sector=False, label="Corredor 2P Oeste",  floor=2)
    G.add_node("STAIR_A_2F", population=0, is_exit=False, is_sector=False, label="Escalera A (2P)",    floor=2)
    G.add_node("STAIR_B_2F", population=0, is_exit=False, is_sector=False, label="Escalera B (2P)",    floor=2)

    G.add_node("S_AULA_201", population=42, is_exit=False, is_sector=True, label="Aula 201",           floor=2)
    G.add_node("S_AULA_202", population=40, is_exit=False, is_sector=True, label="Aula 202",           floor=2)
    G.add_node("S_AULA_203", population=40, is_exit=False, is_sector=True, label="Aula 203",           floor=2)
    G.add_node("S_AULA_204", population=35, is_exit=False, is_sector=True, label="Aula 204",           floor=2)

    def e(u, v, cap, tt):
        G.add_edge(u, v, capacity=cap, travel_time=tt)

    # ── ARISTAS PB ────────────────────────────────────────────────────────────
    # Sectores PB → corredores
    e("S_AULA_001", "CORR_GF_E",  6, 2)
    e("S_AULA_002", "CORR_GF_W",  6, 2)
    e("S_LAB_COMP", "CORR_GF_E",  5, 3)
    e("S_BIBLIO",   "CORR_GF_W",  4, 2)

    # Corredores PB ↔ (conexión lateral + nodos de acceso)
    e("CORR_GF_E", "CORR_GF_W",  6, 4)   # cruce este-oeste
    e("CORR_GF_W", "CORR_GF_E",  6, 4)
    e("CORR_GF_E", "HALL_GF",    8, 3)
    e("CORR_GF_W", "HALL_GF",    8, 3)
    e("CORR_GF_E", "STAIR_A_GF", 4, 2)
    e("CORR_GF_W", "STAIR_B_GF", 4, 2)

    # Pies de escalera → hall / salida lateral
    e("STAIR_A_GF", "HALL_GF",  4, 2)
    e("STAIR_B_GF", "HALL_GF",  3, 2)
    e("STAIR_A_GF", "EXIT_B",   3, 3)   # atajo: escalera A puede salir por EXIT_B

    # Hall → salidas
    e("HALL_GF", "EXIT_A", 5, 1)
    e("HALL_GF", "EXIT_B", 3, 2)

    # ── ARISTAS ESCALERAS (sentido evacuación: bajan) ─────────────────────────
    e("STAIR_A_2F", "STAIR_A_1F", 4, 8)   # capacity 4 p/s, 8 s de recorrido
    e("STAIR_A_1F", "STAIR_A_GF", 4, 8)
    e("STAIR_B_2F", "STAIR_B_1F", 3, 8)
    e("STAIR_B_1F", "STAIR_B_GF", 3, 8)

    # ── ARISTAS 1P ────────────────────────────────────────────────────────────
    e("S_AULA_101",  "CORR_1F_E", 6, 2)
    e("S_AULA_102",  "CORR_1F_E", 6, 3)
    e("S_AULA_103",  "CORR_1F_W", 6, 2)
    e("S_SALA_PROF", "CORR_1F_W", 4, 2)

    e("CORR_1F_E", "CORR_1F_W",  6, 4)
    e("CORR_1F_W", "CORR_1F_E",  6, 4)
    e("CORR_1F_E", "STAIR_A_1F", 4, 2)
    e("CORR_1F_W", "STAIR_B_1F", 3, 2)
    e("STAIR_A_1F", "CORR_1F_E", 4, 2)   # en caso de cruce en 1P
    e("STAIR_B_1F", "CORR_1F_W", 3, 2)

    # ── ARISTAS 2P ────────────────────────────────────────────────────────────
    e("S_AULA_201", "CORR_2F_E", 6, 2)
    e("S_AULA_202", "CORR_2F_E", 6, 3)
    e("S_AULA_203", "CORR_2F_W", 6, 2)
    e("S_AULA_204", "CORR_2F_W", 6, 3)

    e("CORR_2F_E", "CORR_2F_W",  6, 4)
    e("CORR_2F_W", "CORR_2F_E",  6, 4)
    e("CORR_2F_E", "STAIR_A_2F", 4, 2)
    e("CORR_2F_W", "STAIR_B_2F", 3, 2)
    e("STAIR_A_2F", "CORR_2F_E", 4, 2)
    e("STAIR_B_2F", "CORR_2F_W", 3, 2)

    # Salida de emergencia desde 2P (baja capacidad pero camino corto)
    e("CORR_2F_E", "EXIT_C", 2, 3)
    e("CORR_2F_W", "EXIT_C", 2, 3)

    # ── BLOQUEO DE ARISTAS (scenario de emergencia) ───────────────────────────
    if blocked_edges:
        for u, v in blocked_edges:
            if G.has_edge(u, v):
                G.remove_edge(u, v)

    return G


def get_exits(G):
    """Devuelve lista de nodos que son salidas."""
    return [n for n, d in G.nodes(data=True) if d.get("is_exit")]


def get_sectors(G):
    """Devuelve lista de nodos que son sectores con personas."""
    return [n for n, d in G.nodes(data=True) if d.get("is_sector")]


def precompute_routes(G, max_routes_per_sector=5, cutoff=12):
    """
    Para cada sector, precomputa hasta max_routes_per_sector caminos válidos
    hacia cualquier salida, ordenados de menor a mayor tiempo de viaje.

    Args:
        G: grafo del edificio
        max_routes_per_sector: número máximo de rutas a guardar por sector
        cutoff: longitud máxima de caminos (en número de aristas) a explorar

    Returns:
        dict {sector_id: [path_list_1, path_list_2, ...]}}
        donde cada path_list es una lista de nodos [sector, ..., exit].

    Raises:
        ValueError si algún sector no tiene ninguna ruta válida.
    """
    exits = get_exits(G)
    sectors = get_sectors(G)
    routes = {}

    for sector in sectors:
        all_paths = []

        for exit_node in exits:
            try:
                # islice limita la exploración para grafos densos
                paths_gen = nx.all_simple_paths(G, sector, exit_node, cutoff=cutoff)
                candidate_paths = list(islice(paths_gen, max_routes_per_sector * 3))

                # Ordenar por tiempo total de viaje
                def path_time(p):
                    return sum(G[p[i]][p[i + 1]]["travel_time"] for i in range(len(p) - 1))

                candidate_paths.sort(key=path_time)
                all_paths.extend(candidate_paths[:max_routes_per_sector])

            except (nx.NetworkXNoPath, nx.NodeNotFound):
                pass

        # Eliminar duplicados preservando orden
        seen = set()
        unique = []
        for path in all_paths:
            key = tuple(path)
            if key not in seen:
                seen.add(key)
                unique.append(path)

        # Ordenar globalmente por tiempo y tomar las mejores
        unique.sort(key=lambda p: sum(G[p[i]][p[i + 1]]["travel_time"] for i in range(len(p) - 1)))
        routes[sector] = unique[:max_routes_per_sector]

    # Verificar conectividad total
    missing = [s for s in sectors if not routes.get(s)]
    if missing:
        raise ValueError(
            f"Los siguientes sectores no tienen rutas válidas a ninguna salida: {missing}. "
            "Verifique la conectividad del grafo."
        )

    return routes


def route_travel_time(path, G):
    """Calcula el tiempo de viaje total de un camino."""
    return sum(G[path[i]][path[i + 1]]["travel_time"] for i in range(len(path) - 1))


def building_summary(G, routes):
    """Imprime un resumen del edificio y las rutas precomputadas."""
    sectors = get_sectors(G)
    exits = get_exits(G)
    total_pop = sum(G.nodes[s]["population"] for s in sectors)

    print("=" * 60)
    print("RESUMEN DEL EDIFICIO")
    print("=" * 60)
    print(f"  Sectores:        {len(sectors)}")
    print(f"  Salidas:         {len(exits)}  -> {[G.nodes[e]['label'] for e in exits]}")
    print(f"  Nodos totales:   {G.number_of_nodes()}")
    print(f"  Aristas totales: {G.number_of_edges()}")
    print(f"  Población total: {total_pop} personas")
    print()
    print("Rutas precomputadas por sector:")
    for s in sectors:
        lbl = G.nodes[s]["label"]
        pop = G.nodes[s]["population"]
        r_count = len(routes[s])
        times = [route_travel_time(r, G) for r in routes[s]]
        print(f"  {lbl:<22} ({pop:3d}p)  ->  {r_count} rutas  "
              f"[tt mín={min(times)}s, máx={max(times)}s]")
    print("=" * 60)
