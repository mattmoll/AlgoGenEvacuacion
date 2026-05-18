# Optimización Genética de Planes de Evacuación en Edificios Universitarios

**TP2 — Sistemas Inteligentes | UTN FRBA | 1er Cuatrimestre 2026**
**Grupo 6**

| Integrante | Correo |
|---|---|
| Arrascaeta, Santiago | sarrascaeta@frba.utn.edu.ar |
| Canosa, Juan Manuel | jcanosa@frba.utn.edu.ar |
| Dorr, Pedro | pdorr@frba.utn.edu.ar |
| Moll, Matías | mmoll@frba.utn.edu.ar |
| Muhsisoglu, Jorge | jmuhsisoglu@frba.utn.edu.ar |
| Vila Brinusio, Rodrigo | rvilabrinusio@frba.utn.edu.ar |

---

## Descripción del problema

Determinar la asignación óptima de rutas de evacuación para los sectores de un edificio universitario de alta densidad (sede UTN), minimizando el tiempo total de evacuación y los cuellos de botella en pasillos y escaleras.

Se implementa un **Algoritmo Genético desde cero** usando Python puro.

## Estructura del proyecto

```
src/
  building.py       # Modelo del edificio como grafo dirigido (NetworkX)
  simulation.py     # Simulacion discreta de flujo de evacuacion
  ga.py             # Algoritmo Genetico (seleccion, cruce, mutacion, elitismo)
  visualization.py  # Graficos Matplotlib + logs CSV
main.py             # Ejecuta las 5 corridas requeridas
requirements.txt
results/            # Graficos PNG y logs CSV generados por cada corrida
```

## Instalacion

```bash
pip install -r requirements.txt
```

## Ejecucion

```bash
python main.py
```

Los resultados se generan en `results/`.

## Modelo del edificio

El edificio tiene **6 pisos** con distribución **no uniforme** de sectores (refleja la realidad de la sede UTN):

| Piso | Sectores | Descripción |
|------|----------|-------------|
| PB   | 2        | Secretaría, Lab. Cómputo (pocos ocupantes, acceso directo a salidas) |
| 1P   | 3        | Aula 101, Biblioteca, Sala Profesores |
| 2P   | 3        | Aula 201, Aula 202, Lab. Electrónica |
| 3P   | 5        | Aulas 301–305 (pisos de alta densidad de cursada) |
| 4P   | 5        | Aulas 401–405 |
| 5P   | 5        | Aulas 501–505 + Salida de Emergencia |

- **23 sectores**, **792 personas** en total
- **3 salidas**: Salida Principal (5 p/s), Salida Lateral (3 p/s), Salida de Emergencia 5P (2 p/s)
- **2 escaleras** (A y B) recorren los 6 pisos — cuello de botella natural

## Cromosoma

Vector entero de longitud N=23. Cada gen `i` es el indice de la ruta asignada al sector `i`. Las rutas son caminos simples validos en el grafo del edificio, precomputados con NetworkX.

## Funcion de fitness

```
Fitness = 1 / (W1*T_total + W2*D_max + W3*penalty)
```

- **T_total**: tiempo hasta que evacua la ultima persona (makespan)
- **D_max**: densidad maxima en cualquier nodo (penaliza aglomeraciones)
- **penalty**: penalizacion por rutas invalidas o personas no evacuadas

## Corridas

| # | Descripcion | Parametro variado |
|---|---|---|
| 1 | Baseline: torneo k=3, punto unico, mut=10% | — |
| 2 | Alta mutacion (30%) | mutation_rate = 0.30 |
| 3 | Seleccion por ruleta | selection_method = roulette |
| 4 | Prioridad densidad W2=2.0 | W2=2.0 (penaliza cuellos de botella) |
| 5 | Escalera A bloqueada (emergencia) | blocked_edges (todos los tramos de STAIR_A) |

## Stack tecnologico

- **Python 3.x** — implementacion propia del AG (sin librerias de algoritmos evolutivos)
- **NetworkX** — modelado del grafo del edificio
- **NumPy** — operaciones sobre la poblacion
- **Matplotlib** — graficos de evolucion del fitness
- **Pandas** — logs de corridas en CSV
