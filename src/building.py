"""
building.py - Modelado del edificio como grafo dirigido (NetworkX).

Edificio UTN FRBA - Sede Medrano 951 (8 niveles):
  SUB (floor -1): 0 aulas; ~2 depositos/maestranza; Biblioteca Central (flujo ascendente critico)
  PB  (floor  0): 0 aulas; Informes/Seguridad/Mesa de Entradas; Aula Magna
  1P  (floor  1): 20 aulas Serie 100 (101-120); Decanato + Ing. Electrica/Electronica; Secretarias
  2P  (floor  2): 22 aulas Serie 200 (201-222); Oficinas Ciencias Basicas; 4 Labs Computo/Sistemas
  3P  (floor  3): 22 aulas Serie 300 (301-322); Dptpos. Especialidad + SAE; Oficina 309
  4P  (floor  4): 12 aulas Serie 400 (401-412); Bedelia Central; Buffet + CEIT + Fotocopiadora
  5P  (floor  5): 20 aulas Serie 500 (501-520); Boxes atencion posgrado; 2 Labs Computo
  6P  (floor  6): 15 aulas Serie 600 (601-615); 4 of. Mantenimiento/Tecnicas; Salas maquinas/panol

Salidas criticas (PB, floor 0):
  EXIT_A: Puerta Blindex principal Medrano 951  (8 p/s)
  EXIT_B: Porton vehicular Medrano              (5 p/s)
  EXIT_C: Salida trasera Lavalle                (4 p/s)

Dinamica destacada:
  - Subsuelo: Biblioteca sube mientras el resto baja (flujo cruzado critico)
  - 4P: supernodo de congestion (Bedelia + Buffet/CEIT, alta poblacion flotante)
  - 3P: supernodo de congestion medio (SAE + Oficina 309 concentran tramites)
  - 5P: efecto cascada (suma flujo de 6P al propio, caudal duplicado)

Nucleos de escaleras:
  STAIR_A: floors -1 a 6 (nucleo principal A)
  STAIR_B: floors -1 a 6 (nucleo principal B)
  STAIR_C: floors 0 a 3 (tercer nucleo pisos bajos) + STAIR_C_5F (embudo 5P)
  STAIR_SUB: subsuelo -> PB (escalera secundaria de acceso)

Atributos de nodo: population, is_exit, is_sector, label, floor
Atributos de arista: capacity (personas/s) y travel_time (segundos)
"""

import networkx as nx
from itertools import islice


def build_utn_graph(blocked_edges=None):
    """
    Construye el grafo dirigido del edificio UTN FRBA (8 niveles, 3 salidas).

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

    # ── SALIDAS CRITICAS (PB, floor 0) ────────────────────────────────────────
    n("EXIT_A", label="Puerta Principal Medrano 951", is_exit=True, floor=0)
    n("EXIT_B", label="Porton Vehicular Medrano",     is_exit=True, floor=0)
    n("EXIT_C", label="Escape Trasero Lavalle",       is_exit=True, floor=0)

    # ── SUBSUELO (floor -1) ────────────────────────────────────────────────────
    # Sin aulas de cursada. ~2 depositos/maestranza.
    # Biblioteca Central: unica poblacion que SUBE hacia PB (flujo ascendente critico).
    n("CORR_BF_E",  label="Corredor SUB Este",         floor=-1)
    n("CORR_BF_W",  label="Corredor SUB Oeste",        floor=-1)
    n("STAIR_A_BF", label="Escalera A (SUB)",          floor=-1)
    n("STAIR_B_BF", label="Escalera B (SUB)",          floor=-1)
    n("STAIR_SUB",  label="Escalera Secundaria (SUB)", floor=-1)

    n("S_BIBLIO",   population=150, is_sector=True, label="Biblioteca Central UTN FRBA", floor=-1)
    n("S_DEPO_SUB", population=10,  is_sector=True, label="Depositos/Maestranza",        floor=-1)

    e("S_BIBLIO",   "CORR_BF_E", 5, 3)
    e("S_DEPO_SUB", "CORR_BF_W", 3, 2)

    e("CORR_BF_E", "CORR_BF_W",  5, 4)
    e("CORR_BF_W", "CORR_BF_E",  5, 4)
    e("CORR_BF_E", "STAIR_A_BF", 4, 2)
    e("CORR_BF_W", "STAIR_B_BF", 4, 2)
    e("CORR_BF_E", "STAIR_SUB",  3, 2)
    e("CORR_BF_W", "STAIR_SUB",  3, 2)

    # ── PLANTA BAJA (floor 0) — ZONA DE SUMIDEROS FINALES ─────────────────────
    # Sin aulas. Informes/Seguridad/Mesa de Entradas + Aula Magna.
    # Tres salidas criticas a la via publica.
    n("HALL_GF",    label="Hall Principal PB",   floor=0)
    n("CORR_GF_E",  label="Corredor PB Este",    floor=0)
    n("CORR_GF_W",  label="Corredor PB Oeste",   floor=0)
    n("CORR_GF_C",  label="Corredor PB Central", floor=0)
    n("STAIR_A_GF", label="Escalera A (PB)",     floor=0)
    n("STAIR_B_GF", label="Escalera B (PB)",     floor=0)
    n("STAIR_C_GF", label="Escalera C (PB)",     floor=0)

    n("S_INFORMES",   population=15,  is_sector=True, label="Informes/Seguridad/Mesa Entrada", floor=0)
    n("S_AULA_MAGNA", population=200, is_sector=True, label="Aula Magna",                      floor=0)

    e("S_INFORMES",   "CORR_GF_E", 4, 2)
    e("S_AULA_MAGNA", "CORR_GF_C", 5, 3)

    e("CORR_GF_E", "HALL_GF",    8, 2)
    e("CORR_GF_W", "HALL_GF",    8, 2)
    e("CORR_GF_C", "CORR_GF_E",  6, 2)
    e("CORR_GF_C", "CORR_GF_W",  6, 2)
    e("CORR_GF_E", "CORR_GF_C",  6, 2)
    e("CORR_GF_W", "CORR_GF_C",  6, 2)

    e("STAIR_A_GF", "HALL_GF",    5, 2)
    e("STAIR_B_GF", "CORR_GF_E",  4, 2)
    e("STAIR_C_GF", "CORR_GF_W",  4, 2)
    e("CORR_GF_E",  "STAIR_A_GF", 5, 2)
    e("CORR_GF_E",  "STAIR_B_GF", 4, 2)
    e("CORR_GF_W",  "STAIR_C_GF", 4, 2)

    # Salidas desde Hall y corredores
    e("HALL_GF",   "EXIT_A", 8, 1)
    e("CORR_GF_E", "EXIT_B", 5, 2)
    e("CORR_GF_W", "EXIT_C", 4, 2)

    # ── PRIMER PISO (floor 1) — 3 nucleos + pasillo central ───────────────────
    # 20 aulas Serie 100 (101-120): 4 grupos x5 aulas.
    # Decanato + Dpto. Ing. Electrica/Electronica; Oficinas de Secretarias.
    n("CORR_1F_E",  label="Corredor 1P Este",    floor=1)
    n("CORR_1F_W",  label="Corredor 1P Oeste",   floor=1)
    n("CORR_1F_C",  label="Corredor 1P Central", floor=1)
    n("STAIR_A_1F", label="Escalera A (1P)",     floor=1)
    n("STAIR_B_1F", label="Escalera B (1P)",     floor=1)
    n("STAIR_C_1F", label="Escalera C (1P)",     floor=1)

    n("S_AULAS_1F_A",  population=175, is_sector=True, label="Aulas 100s A (101-105)",    floor=1)
    n("S_AULAS_1F_B",  population=175, is_sector=True, label="Aulas 100s B (106-110)",    floor=1)
    n("S_AULAS_1F_C",  population=175, is_sector=True, label="Aulas 100s C (111-115)",    floor=1)
    n("S_AULAS_1F_D",  population=175, is_sector=True, label="Aulas 100s D (116-120)",    floor=1)
    n("S_DECANATO_1F", population=30,  is_sector=True, label="Decanato + Ing. Electrica", floor=1)
    n("S_SECRET_1F",   population=40,  is_sector=True, label="Oficinas Secretarias",      floor=1)

    e("S_AULAS_1F_A",  "CORR_1F_E", 6, 2)
    e("S_AULAS_1F_B",  "CORR_1F_E", 6, 2)
    e("S_AULAS_1F_C",  "CORR_1F_W", 6, 2)
    e("S_AULAS_1F_D",  "CORR_1F_W", 6, 2)
    e("S_DECANATO_1F", "CORR_1F_W", 4, 2)
    e("S_SECRET_1F",   "CORR_1F_C", 4, 2)

    e("CORR_1F_E", "CORR_1F_C",  6, 3)
    e("CORR_1F_W", "CORR_1F_C",  6, 3)
    e("CORR_1F_C", "CORR_1F_E",  6, 3)
    e("CORR_1F_C", "CORR_1F_W",  6, 3)
    e("CORR_1F_E", "STAIR_A_1F", 5, 2)
    e("CORR_1F_W", "STAIR_B_1F", 5, 2)
    e("CORR_1F_C", "STAIR_C_1F", 5, 2)
    e("STAIR_A_1F", "CORR_1F_E", 5, 2)
    e("STAIR_B_1F", "CORR_1F_W", 5, 2)
    e("STAIR_C_1F", "CORR_1F_C", 5, 2)

    # ── SEGUNDO PISO (floor 2) — flujo descendente continuo ───────────────────
    # 22 aulas Serie 200 (201-222): 5 grupos. Oficinas menores Ciencias Basicas.
    # 4 Laboratorios de Computo/Sistemas. Pasillo central recibe toda la carga superior.
    n("CORR_2F_E",  label="Corredor 2P Este",    floor=2)
    n("CORR_2F_W",  label="Corredor 2P Oeste",   floor=2)
    n("CORR_2F_C",  label="Corredor 2P Central", floor=2)
    n("STAIR_A_2F", label="Escalera A (2P)",     floor=2)
    n("STAIR_B_2F", label="Escalera B (2P)",     floor=2)
    n("STAIR_C_2F", label="Escalera C (2P)",     floor=2)

    n("S_AULAS_2F_A",  population=175, is_sector=True, label="Aulas 200s A (201-205)", floor=2)
    n("S_AULAS_2F_B",  population=175, is_sector=True, label="Aulas 200s B (206-210)", floor=2)
    n("S_AULAS_2F_C",  population=175, is_sector=True, label="Aulas 200s C (211-215)", floor=2)
    n("S_AULAS_2F_D",  population=140, is_sector=True, label="Aulas 200s D (216-219)", floor=2)
    n("S_AULAS_2F_E",  population=105, is_sector=True, label="Aulas 200s E (220-222)", floor=2)
    n("S_CB_OFFICES",  population=20,  is_sector=True, label="Oficinas Ciencias Basicas", floor=2)
    n("S_LAB_SIS_A",   population=25,  is_sector=True, label="Lab. Computo/Sistemas A",  floor=2)
    n("S_LAB_SIS_B",   population=25,  is_sector=True, label="Lab. Computo/Sistemas B",  floor=2)
    n("S_LAB_SIS_C",   population=25,  is_sector=True, label="Lab. Computo/Sistemas C",  floor=2)
    n("S_LAB_SIS_D",   population=25,  is_sector=True, label="Lab. Computo/Sistemas D",  floor=2)

    e("S_AULAS_2F_A",  "CORR_2F_E", 6, 2)
    e("S_AULAS_2F_B",  "CORR_2F_E", 6, 2)
    e("S_AULAS_2F_C",  "CORR_2F_W", 6, 2)
    e("S_AULAS_2F_D",  "CORR_2F_W", 6, 2)
    e("S_AULAS_2F_E",  "CORR_2F_C", 6, 2)
    e("S_CB_OFFICES",  "CORR_2F_W", 4, 2)
    e("S_LAB_SIS_A",   "CORR_2F_E", 4, 3)
    e("S_LAB_SIS_B",   "CORR_2F_E", 4, 3)
    e("S_LAB_SIS_C",   "CORR_2F_C", 4, 3)
    e("S_LAB_SIS_D",   "CORR_2F_C", 4, 3)

    e("CORR_2F_E", "CORR_2F_C",  6, 3)
    e("CORR_2F_W", "CORR_2F_C",  6, 3)
    e("CORR_2F_C", "CORR_2F_E",  6, 3)
    e("CORR_2F_C", "CORR_2F_W",  6, 3)
    e("CORR_2F_E", "STAIR_A_2F", 5, 2)
    e("CORR_2F_W", "STAIR_B_2F", 5, 2)
    e("CORR_2F_C", "STAIR_C_2F", 5, 2)
    e("STAIR_A_2F", "CORR_2F_E", 5, 2)
    e("STAIR_B_2F", "CORR_2F_W", 5, 2)
    e("STAIR_C_2F", "CORR_2F_C", 5, 2)

    # ── TERCER PISO (floor 3) — supernodo de congestion medio ─────────────────
    # 22 aulas Serie 300 (301-322): 5 grupos. Casi todos los Departamentos de
    # Especialidad + SAE. Oficina 309: tramites generales, hiperconcurrida.
    n("CORR_3F_E",  label="Corredor 3P Este",    floor=3)
    n("CORR_3F_W",  label="Corredor 3P Oeste",   floor=3)
    n("CORR_3F_C",  label="Corredor 3P Central", floor=3)
    n("STAIR_A_3F", label="Escalera A (3P)",     floor=3)
    n("STAIR_B_3F", label="Escalera B (3P)",     floor=3)
    n("STAIR_C_3F", label="Escalera C (3P)",     floor=3)

    n("S_AULAS_3F_A",  population=175, is_sector=True, label="Aulas 300s A (301-305)",    floor=3)
    n("S_AULAS_3F_B",  population=175, is_sector=True, label="Aulas 300s B (306-310)",    floor=3)
    n("S_AULAS_3F_C",  population=175, is_sector=True, label="Aulas 300s C (311-315)",    floor=3)
    n("S_AULAS_3F_D",  population=140, is_sector=True, label="Aulas 300s D (316-319)",    floor=3)
    n("S_AULAS_3F_E",  population=105, is_sector=True, label="Aulas 300s E (320-322)",    floor=3)
    n("S_DPTPS_ESP",   population=60,  is_sector=True, label="Dptpos. Especialidad + SAE", floor=3)
    n("S_OFIC_309",    population=60,  is_sector=True, label="Oficina 309 (tramites)",     floor=3)

    e("S_AULAS_3F_A",  "CORR_3F_E", 6, 2)
    e("S_AULAS_3F_B",  "CORR_3F_E", 6, 2)
    e("S_AULAS_3F_C",  "CORR_3F_W", 6, 2)
    e("S_AULAS_3F_D",  "CORR_3F_W", 6, 2)
    e("S_AULAS_3F_E",  "CORR_3F_C", 6, 2)
    e("S_DPTPS_ESP",   "CORR_3F_C", 4, 2)
    e("S_OFIC_309",    "CORR_3F_C", 4, 2)

    e("CORR_3F_E", "CORR_3F_C",  6, 3)
    e("CORR_3F_W", "CORR_3F_C",  6, 3)
    e("CORR_3F_C", "CORR_3F_E",  6, 3)
    e("CORR_3F_C", "CORR_3F_W",  6, 3)
    e("CORR_3F_E", "STAIR_A_3F", 5, 2)
    e("CORR_3F_W", "STAIR_B_3F", 5, 2)
    e("CORR_3F_C", "STAIR_C_3F", 5, 2)
    e("STAIR_A_3F", "CORR_3F_E", 5, 2)
    e("STAIR_B_3F", "CORR_3F_W", 5, 2)
    e("STAIR_C_3F", "CORR_3F_C", 5, 2)

    # ── CUARTO PISO (floor 4) — supernodo de congestion superior ──────────────
    # 12 aulas Serie 400 (401-412): 3 grupos. Bedelia Central.
    # Buffet + CEIT + Fotocopiadora: alta poblacion flotante, cuello de botella.
    n("CORR_4F_E",  label="Corredor 4P Este",  floor=4)
    n("CORR_4F_W",  label="Corredor 4P Oeste", floor=4)
    n("STAIR_A_4F", label="Escalera A (4P)",   floor=4)
    n("STAIR_B_4F", label="Escalera B (4P)",   floor=4)

    n("S_AULAS_4F_A",  population=175, is_sector=True, label="Aulas 400s A (401-405)",       floor=4)
    n("S_AULAS_4F_B",  population=175, is_sector=True, label="Aulas 400s B (406-410)",       floor=4)
    n("S_AULAS_4F_C",  population=70,  is_sector=True, label="Aulas 400s C (411-412)",       floor=4)
    n("S_BEDELIA_4F",  population=60,  is_sector=True, label="Bedelia Central",              floor=4)
    n("S_BUFFET_CEIT", population=100, is_sector=True, label="Buffet + CEIT + Fotocopiadora", floor=4)

    e("S_AULAS_4F_A",  "CORR_4F_E", 6, 2)
    e("S_AULAS_4F_B",  "CORR_4F_E", 6, 2)
    e("S_AULAS_4F_C",  "CORR_4F_W", 5, 2)
    e("S_BEDELIA_4F",  "CORR_4F_W", 4, 2)
    e("S_BUFFET_CEIT", "CORR_4F_E", 4, 2)

    e("CORR_4F_E", "CORR_4F_W",  5, 4)
    e("CORR_4F_W", "CORR_4F_E",  5, 4)
    e("CORR_4F_E", "STAIR_A_4F", 5, 2)
    e("CORR_4F_W", "STAIR_B_4F", 5, 2)
    e("STAIR_A_4F", "CORR_4F_E", 5, 2)
    e("STAIR_B_4F", "CORR_4F_W", 5, 2)

    # ── QUINTO PISO (floor 5) — efecto cascada + 3 nucleos EMBUDO ─────────────
    # 20 aulas Serie 500 (501-520): 4 grupos x5. Boxes de atencion (Inscripcion Posgrado).
    # 2 Labs de Computo. El caudal se duplica al sumarse el flujo de 6P.
    # STAIR_C_5F: tercer nucleo embudo, canaliza hacia STAIR_A_4F al descender.
    n("CORR_5F_E",  label="Corredor 5P Este",       floor=5)
    n("CORR_5F_W",  label="Corredor 5P Oeste",      floor=5)
    n("CORR_5F_C",  label="Corredor 5P Central",    floor=5)
    n("STAIR_A_5F", label="Escalera A (5P)",        floor=5)
    n("STAIR_B_5F", label="Escalera B (5P)",        floor=5)
    n("STAIR_C_5F", label="Escalera C/Embudo (5P)", floor=5)

    n("S_AULAS_5F_A",   population=175, is_sector=True, label="Aulas 500s A (501-505)",  floor=5)
    n("S_AULAS_5F_B",   population=175, is_sector=True, label="Aulas 500s B (506-510)",  floor=5)
    n("S_AULAS_5F_C",   population=175, is_sector=True, label="Aulas 500s C (511-515)",  floor=5)
    n("S_AULAS_5F_D",   population=175, is_sector=True, label="Aulas 500s D (516-520)",  floor=5)
    n("S_BOXES_5F",     population=30,  is_sector=True, label="Boxes Inscripcion Posgrado", floor=5)
    n("S_LAB_COMP5F_A", population=25,  is_sector=True, label="Lab. Computo Posgrado A", floor=5)
    n("S_LAB_COMP5F_B", population=25,  is_sector=True, label="Lab. Computo Posgrado B", floor=5)

    e("S_AULAS_5F_A",   "CORR_5F_E", 6, 2)
    e("S_AULAS_5F_B",   "CORR_5F_E", 6, 2)
    e("S_AULAS_5F_C",   "CORR_5F_W", 6, 2)
    e("S_AULAS_5F_D",   "CORR_5F_W", 6, 2)
    e("S_BOXES_5F",     "CORR_5F_C", 4, 2)
    e("S_LAB_COMP5F_A", "CORR_5F_E", 4, 3)
    e("S_LAB_COMP5F_B", "CORR_5F_C", 4, 3)

    e("CORR_5F_E", "CORR_5F_C",  6, 3)
    e("CORR_5F_W", "CORR_5F_C",  6, 3)
    e("CORR_5F_C", "CORR_5F_E",  6, 3)
    e("CORR_5F_C", "CORR_5F_W",  6, 3)
    e("CORR_5F_E", "STAIR_A_5F", 5, 2)
    e("CORR_5F_W", "STAIR_B_5F", 5, 2)
    e("CORR_5F_C", "STAIR_C_5F", 5, 2)
    e("STAIR_A_5F", "CORR_5F_E", 5, 2)
    e("STAIR_B_5F", "CORR_5F_W", 5, 2)
    e("STAIR_C_5F", "CORR_5F_C", 5, 2)

    # ── SEXTO PISO (floor 6) — inicio del flujo, descenso puro ───────────────
    # 15 aulas Serie 600 (601-615): 3 grupos x5. 4 of. Mantenimiento/Tecnicas.
    # Salas de maquinas y panol. Solo desciende por escaleras hacia 5P.
    n("CORR_6F_E",  label="Corredor 6P Este",  floor=6)
    n("CORR_6F_W",  label="Corredor 6P Oeste", floor=6)
    n("STAIR_A_6F", label="Escalera A (6P)",   floor=6)
    n("STAIR_B_6F", label="Escalera B (6P)",   floor=6)

    n("S_AULAS_6F_A",  population=175, is_sector=True, label="Aulas 600s A (601-605)",       floor=6)
    n("S_AULAS_6F_B",  population=175, is_sector=True, label="Aulas 600s B (606-610)",       floor=6)
    n("S_AULAS_6F_C",  population=175, is_sector=True, label="Aulas 600s C (611-615)",       floor=6)
    n("S_TECNICAS_6F", population=20,  is_sector=True, label="Of. Mantenimiento/Tecnicas",   floor=6)
    n("S_LAB_MAQUI",   population=10,  is_sector=True, label="Salas Maquinas/Panel",        floor=6)

    e("S_AULAS_6F_A",  "CORR_6F_E", 6, 2)
    e("S_AULAS_6F_B",  "CORR_6F_W", 6, 2)
    e("S_AULAS_6F_C",  "CORR_6F_E", 6, 2)
    e("S_TECNICAS_6F", "CORR_6F_W", 4, 2)
    e("S_LAB_MAQUI",   "CORR_6F_W", 3, 3)

    e("CORR_6F_E", "CORR_6F_W",  5, 4)
    e("CORR_6F_W", "CORR_6F_E",  5, 4)
    e("CORR_6F_E", "STAIR_A_6F", 5, 2)
    e("CORR_6F_W", "STAIR_B_6F", 5, 2)
    e("STAIR_A_6F", "CORR_6F_E", 5, 2)
    e("STAIR_B_6F", "CORR_6F_W", 5, 2)

    # ── ESCALERAS VERTICALES ──────────────────────────────────────────────────
    # STAIR_A y STAIR_B: descienden 6P → 5P → ... → 1P → PB → SUB
    for floor_n in range(5, -1, -1):
        upper = f"{floor_n + 1}F"
        lower = f"{floor_n}F" if floor_n > 0 else "GF"
        e(f"STAIR_A_{upper}", f"STAIR_A_{lower}", 5, 50)
        e(f"STAIR_B_{upper}", f"STAIR_B_{lower}", 4, 50)

    # STAIR_A y STAIR_B continuan hasta el subsuelo
    e("STAIR_A_GF", "STAIR_A_BF", 5, 50)
    e("STAIR_B_GF", "STAIR_B_BF", 4, 50)

    # STAIR_C: descends 3P → 2P → 1P → PB (tercer nucleo pisos bajos)
    for floor_n in range(2, -1, -1):
        upper = f"{floor_n + 1}F"
        lower = f"{floor_n}F" if floor_n > 0 else "GF"
        e(f"STAIR_C_{upper}", f"STAIR_C_{lower}", 4, 50)

    # STAIR_C_5F (embudo): canaliza flujo de 5P hacia STAIR_A de 4P
    e("STAIR_C_5F", "STAIR_A_4F", 4, 50)

    # STAIR_SUB: escalera secundaria del subsuelo sube a PB
    e("STAIR_SUB", "STAIR_A_GF", 3, 50)

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


def precompute_routes(G, max_routes_per_sector=5, cutoff=20):
    """
    Para cada sector, precomputa hasta max_routes_per_sector caminos validos
    hacia cualquier salida, ordenados de menor a mayor tiempo de viaje.

    Args:
        G: grafo del edificio
        max_routes_per_sector: numero maximo de rutas a guardar por sector
        cutoff: longitud maxima de caminos en aristas (20 cubre 6P -> EXIT_A)

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
    print("RESUMEN DEL EDIFICIO UTN FRBA — Sede Medrano 951")
    print("=" * 65)
    print(f"  Sectores:        {len(sectors)}")
    print(f"  Salidas:         {len(exits)}  -> {[G.nodes[ex]['label'] for ex in exits]}")
    print(f"  Nodos totales:   {G.number_of_nodes()}")
    print(f"  Aristas totales: {G.number_of_edges()}")
    print(f"  Poblacion total: {total_pop} personas")
    print()

    floor_labels = {
        -1: "SUB",
         0: "PB",
         1: "1P",
         2: "2P",
         3: "3P",
         4: "4P",
         5: "5P",
         6: "6P",
    }
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
            print(f"    {lbl:<32} ({pop:3d}p)  {r_count} rutas  "
                  f"[tt min={min(times)}s, max={max(times)}s]")

    print("=" * 65)
