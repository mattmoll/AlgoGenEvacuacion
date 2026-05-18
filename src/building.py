"""
building.py - Modelado del edificio como grafo dirigido (NetworkX).

Representa la sede UTN (6 pisos) con distribucion no uniforme de aulas:
  - Pisos 0-2 (PB, 1P, 2P): pocos sectores (secretaria, labs, biblioteca)
  - Pisos 3-5 (3P, 4P, 5P): muchos sectores (aulas grandes de cursada)

Atributos de nodo: population, is_exit, is_sector, label, floor
Atributos de arista: capacity (personas/s) y travel_time (segundos)
"""

import networkx as nx
from itertools import islice


def build_utn_graph(blocked_edges=None):
    """
    Construye el grafo dirigido del edificio UTN (6 pisos, 18 sectores, 3 salidas).

    Distribucion de sectores (no uniforme por diseno):
      PB  (floor 0): 2 sectores  - Secretaria, Lab Computo
      1P  (floor 1): 3 sectores  - Aula 101, Biblioteca, Sala Profesores
      2P  (floor 2): 3 sectores  - Aula 201, Aula 202, Lab Electronica
      3P  (floor 3): 5 sectores  - Aulas 301-305  (pisos de alta densidad)
      4P  (floor 4): 5 sectores  - Aulas 401-405
      5P  (floor 5): 5 sectores  - Aulas 501-505 + EXIT_C (salida emergencia)

    Salidas:
      EXIT_A: Salida Principal  (5 p/s) - PB
      EXIT_B: Salida Lateral    (3 p/s) - PB
      EXIT_C: Salida Emergencia (2 p/s) - 5P

    Escaleras A y B recorren los 6 pisos (0-5).

    Args:
        blocked_edges: lista de tuplas (u, v) a eliminar del grafo.

    Returns:
        G: nx.DiGraph con el edificio modelado.
    """
    G = nx.DiGraph()

    def n(node_id, population=0, is_exit=False, is_sector=False, label="", floor=0):
        G.add_node(node_id, population=population, is_exit=is_exit,
                   is_sector=is_sector, label=label, floor=floor)

    def e(u, v, cap, tt):
        G.add_edge(u, v, capacity=cap, travel_time=tt)

    # ── SALIDAS ───────────────────────────────────────────────────────────────
    n("EXIT_A", label="Salida Principal",   is_exit=True, floor=0)
    n("EXIT_B", label="Salida Lateral",     is_exit=True, floor=0)
    n("EXIT_C", label="Salida Emergencia",  is_exit=True, floor=5)

    # ── PLANTA BAJA (floor 0) — 2 sectores ───────────────────────────────────
    n("HALL_GF",    label="Hall PB",            floor=0)
    n("CORR_0F_E",  label="Corredor PB Este",   floor=0)
    n("CORR_0F_W",  label="Corredor PB Oeste",  floor=0)
    n("STAIR_A_0F", label="Escalera A (PB)",    floor=0)
    n("STAIR_B_0F", label="Escalera B (PB)",    floor=0)

    n("S_SECRET",   population=20, is_sector=True, label="Secretaria",   floor=0)
    n("S_LAB_COMP", population=22, is_sector=True, label="Lab. Computo", floor=0)

    e("S_SECRET",   "CORR_0F_W", 5, 2)
    e("S_LAB_COMP", "CORR_0F_E", 5, 3)

    e("CORR_0F_E", "CORR_0F_W",  6, 3)
    e("CORR_0F_W", "CORR_0F_E",  6, 3)
    e("CORR_0F_E", "HALL_GF",    8, 2)
    e("CORR_0F_W", "HALL_GF",    8, 2)
    e("CORR_0F_E", "STAIR_A_0F", 4, 2)
    e("CORR_0F_W", "STAIR_B_0F", 4, 2)

    e("STAIR_A_0F", "HALL_GF", 4, 2)
    e("STAIR_B_0F", "HALL_GF", 3, 2)
    e("STAIR_A_0F", "EXIT_B",  3, 2)

    e("HALL_GF", "EXIT_A", 5, 1)
    e("HALL_GF", "EXIT_B", 3, 2)

    # ── PRIMER PISO (floor 1) — 3 sectores ───────────────────────────────────
    n("CORR_1F_E",  label="Corredor 1P Este",   floor=1)
    n("CORR_1F_W",  label="Corredor 1P Oeste",  floor=1)
    n("STAIR_A_1F", label="Escalera A (1P)",    floor=1)
    n("STAIR_B_1F", label="Escalera B (1P)",    floor=1)

    n("S_AULA_101",  population=28, is_sector=True, label="Aula 101",        floor=1)
    n("S_BIBLIO",    population=32, is_sector=True, label="Biblioteca",       floor=1)
    n("S_SALA_PROF", population=12, is_sector=True, label="Sala Profesores", floor=1)

    e("S_AULA_101",  "CORR_1F_E", 5, 2)
    e("S_BIBLIO",    "CORR_1F_W", 4, 3)
    e("S_SALA_PROF", "CORR_1F_W", 3, 2)

    e("CORR_1F_E", "CORR_1F_W",  6, 3)
    e("CORR_1F_W", "CORR_1F_E",  6, 3)
    e("CORR_1F_E", "STAIR_A_1F", 4, 2)
    e("CORR_1F_W", "STAIR_B_1F", 4, 2)
    e("STAIR_A_1F", "CORR_1F_E", 4, 2)
    e("STAIR_B_1F", "CORR_1F_W", 3, 2)

    # ── SEGUNDO PISO (floor 2) — 3 sectores ──────────────────────────────────
    n("CORR_2F_E",  label="Corredor 2P Este",   floor=2)
    n("CORR_2F_W",  label="Corredor 2P Oeste",  floor=2)
    n("STAIR_A_2F", label="Escalera A (2P)",    floor=2)
    n("STAIR_B_2F", label="Escalera B (2P)",    floor=2)

    n("S_AULA_201",    population=32, is_sector=True, label="Aula 201",         floor=2)
    n("S_AULA_202",    population=30, is_sector=True, label="Aula 202",         floor=2)
    n("S_LAB_ELECTRO", population=25, is_sector=True, label="Lab. Electronica", floor=2)

    e("S_AULA_201",    "CORR_2F_E", 5, 2)
    e("S_AULA_202",    "CORR_2F_E", 5, 3)
    e("S_LAB_ELECTRO", "CORR_2F_W", 4, 2)

    e("CORR_2F_E", "CORR_2F_W",  6, 3)
    e("CORR_2F_W", "CORR_2F_E",  6, 3)
    e("CORR_2F_E", "STAIR_A_2F", 4, 2)
    e("CORR_2F_W", "STAIR_B_2F", 4, 2)
    e("STAIR_A_2F", "CORR_2F_E", 4, 2)
    e("STAIR_B_2F", "CORR_2F_W", 3, 2)

    # ── TERCER PISO (floor 3) — 5 sectores ───────────────────────────────────
    n("CORR_3F_E",  label="Corredor 3P Este",   floor=3)
    n("CORR_3F_W",  label="Corredor 3P Oeste",  floor=3)
    n("STAIR_A_3F", label="Escalera A (3P)",    floor=3)
    n("STAIR_B_3F", label="Escalera B (3P)",    floor=3)

    n("S_AULA_301", population=42, is_sector=True, label="Aula 301", floor=3)
    n("S_AULA_302", population=42, is_sector=True, label="Aula 302", floor=3)
    n("S_AULA_303", population=40, is_sector=True, label="Aula 303", floor=3)
    n("S_AULA_304", population=38, is_sector=True, label="Aula 304", floor=3)
    n("S_AULA_305", population=35, is_sector=True, label="Aula 305", floor=3)

    e("S_AULA_301", "CORR_3F_E", 6, 2)
    e("S_AULA_302", "CORR_3F_E", 6, 3)
    e("S_AULA_303", "CORR_3F_E", 6, 2)
    e("S_AULA_304", "CORR_3F_W", 6, 2)
    e("S_AULA_305", "CORR_3F_W", 6, 3)

    e("CORR_3F_E", "CORR_3F_W",  6, 4)
    e("CORR_3F_W", "CORR_3F_E",  6, 4)
    e("CORR_3F_E", "STAIR_A_3F", 4, 2)
    e("CORR_3F_W", "STAIR_B_3F", 4, 2)
    e("STAIR_A_3F", "CORR_3F_E", 4, 2)
    e("STAIR_B_3F", "CORR_3F_W", 3, 2)

    # ── CUARTO PISO (floor 4) — 5 sectores ───────────────────────────────────
    n("CORR_4F_E",  label="Corredor 4P Este",   floor=4)
    n("CORR_4F_W",  label="Corredor 4P Oeste",  floor=4)
    n("STAIR_A_4F", label="Escalera A (4P)",    floor=4)
    n("STAIR_B_4F", label="Escalera B (4P)",    floor=4)

    n("S_AULA_401", population=42, is_sector=True, label="Aula 401", floor=4)
    n("S_AULA_402", population=42, is_sector=True, label="Aula 402", floor=4)
    n("S_AULA_403", population=40, is_sector=True, label="Aula 403", floor=4)
    n("S_AULA_404", population=38, is_sector=True, label="Aula 404", floor=4)
    n("S_AULA_405", population=35, is_sector=True, label="Aula 405", floor=4)

    e("S_AULA_401", "CORR_4F_E", 6, 2)
    e("S_AULA_402", "CORR_4F_E", 6, 3)
    e("S_AULA_403", "CORR_4F_E", 6, 2)
    e("S_AULA_404", "CORR_4F_W", 6, 2)
    e("S_AULA_405", "CORR_4F_W", 6, 3)

    e("CORR_4F_E", "CORR_4F_W",  6, 4)
    e("CORR_4F_W", "CORR_4F_E",  6, 4)
    e("CORR_4F_E", "STAIR_A_4F", 4, 2)
    e("CORR_4F_W", "STAIR_B_4F", 4, 2)
    e("STAIR_A_4F", "CORR_4F_E", 4, 2)
    e("STAIR_B_4F", "CORR_4F_W", 3, 2)

    # ── QUINTO PISO (floor 5) — 5 sectores + EXIT_C ───────────────────────────
    n("CORR_5F_E",  label="Corredor 5P Este",   floor=5)
    n("CORR_5F_W",  label="Corredor 5P Oeste",  floor=5)
    n("STAIR_A_5F", label="Escalera A (5P)",    floor=5)
    n("STAIR_B_5F", label="Escalera B (5P)",    floor=5)

    n("S_AULA_501", population=42, is_sector=True, label="Aula 501", floor=5)
    n("S_AULA_502", population=42, is_sector=True, label="Aula 502", floor=5)
    n("S_AULA_503", population=40, is_sector=True, label="Aula 503", floor=5)
    n("S_AULA_504", population=38, is_sector=True, label="Aula 504", floor=5)
    n("S_AULA_505", population=35, is_sector=True, label="Aula 505", floor=5)

    e("S_AULA_501", "CORR_5F_E", 6, 2)
    e("S_AULA_502", "CORR_5F_E", 6, 3)
    e("S_AULA_503", "CORR_5F_E", 6, 2)
    e("S_AULA_504", "CORR_5F_W", 6, 2)
    e("S_AULA_505", "CORR_5F_W", 6, 3)

    e("CORR_5F_E", "CORR_5F_W",  6, 4)
    e("CORR_5F_W", "CORR_5F_E",  6, 4)
    e("CORR_5F_E", "STAIR_A_5F", 4, 2)
    e("CORR_5F_W", "STAIR_B_5F", 4, 2)
    e("STAIR_A_5F", "CORR_5F_E", 4, 2)
    e("STAIR_B_5F", "CORR_5F_W", 3, 2)

    # Salida de emergencia desde 5P
    e("CORR_5F_E", "EXIT_C", 2, 3)
    e("CORR_5F_W", "EXIT_C", 2, 3)

    # ── ESCALERAS VERTICALES (bajan: piso N -> piso N-1) ─────────────────────
    for floor in range(4, -1, -1):
        upper = floor + 1
        lower = floor
        e(f"STAIR_A_{upper}F", f"STAIR_A_{lower}F", 4, 10)
        e(f"STAIR_B_{upper}F", f"STAIR_B_{lower}F", 3, 10)

    # ── BLOQUEO DE ARISTAS ────────────────────────────────────────────────────
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


def precompute_routes(G, max_routes_per_sector=5, cutoff=14):
    """
    Para cada sector, precomputa hasta max_routes_per_sector caminos validos
    hacia cualquier salida, ordenados de menor a mayor tiempo de viaje.

    Args:
        G: grafo del edificio
        max_routes_per_sector: numero maximo de rutas a guardar por sector
        cutoff: longitud maxima de caminos en aristas (14 cubre 5P -> EXIT_A)

    Returns:
        dict {sector_id: [path_list_1, path_list_2, ...]}

    Raises:
        ValueError si algun sector no tiene ninguna ruta valida.
    """
    exits = get_exits(G)
    sectors = get_sectors(G)
    routes = {}

    for sector in sectors:
        all_paths = []

        for exit_node in exits:
            try:
                paths_gen = nx.all_simple_paths(G, sector, exit_node, cutoff=cutoff)
                candidate_paths = list(islice(paths_gen, max_routes_per_sector * 3))

                def path_time(p):
                    return sum(G[p[i]][p[i + 1]]["travel_time"] for i in range(len(p) - 1))

                candidate_paths.sort(key=path_time)
                all_paths.extend(candidate_paths[:max_routes_per_sector])

            except (nx.NetworkXNoPath, nx.NodeNotFound):
                pass

        seen = set()
        unique = []
        for path in all_paths:
            key = tuple(path)
            if key not in seen:
                seen.add(key)
                unique.append(path)

        unique.sort(key=lambda p: sum(G[p[i]][p[i + 1]]["travel_time"] for i in range(len(p) - 1)))
        routes[sector] = unique[:max_routes_per_sector]

    missing = [s for s in sectors if not routes.get(s)]
    if missing:
        raise ValueError(
            f"Los siguientes sectores no tienen rutas validas a ninguna salida: {missing}. "
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

    print("=" * 65)
    print("RESUMEN DEL EDIFICIO (6 pisos, distribucion no uniforme)")
    print("=" * 65)
    print(f"  Sectores:        {len(sectors)}")
    print(f"  Salidas:         {len(exits)}  -> {[G.nodes[ex]['label'] for ex in exits]}")
    print(f"  Nodos totales:   {G.number_of_nodes()}")
    print(f"  Aristas totales: {G.number_of_edges()}")
    print(f"  Poblacion total: {total_pop} personas")
    print()

    floor_labels = {0: "PB", 1: "1P", 2: "2P", 3: "3P", 4: "4P", 5: "5P"}
    for floor_n in sorted(floor_labels.keys()):
        floor_sectors = [s for s in sectors if G.nodes[s]["floor"] == floor_n]
        if not floor_sectors:
            continue
        floor_pop = sum(G.nodes[s]["population"] for s in floor_sectors)
        print(f"  Piso {floor_labels[floor_n]} ({len(floor_sectors)} sectores, {floor_pop}p):")
        for s in floor_sectors:
            lbl = G.nodes[s]["label"]
            pop = G.nodes[s]["population"]
            r_count = len(routes[s])
            times = [route_travel_time(r, G) for r in routes[s]]
            print(f"    {lbl:<24} ({pop:3d}p)  {r_count} rutas  "
                  f"[tt min={min(times)}s, max={max(times)}s]")

    print("=" * 65)
