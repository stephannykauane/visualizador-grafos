from collections import deque


def bfs_steps(graph, start):
    if start not in graph.nodes:
        return []

    visited = []
    queue = [start]
    discovered = [start]
    traversed_edges = []

    steps = []

    steps.append({
        "current": start,
        "current_neighbor": None,
        "visited": [],
        "discovered": list(discovered),
        "queue": list(queue),
        "traversed_edges": [],
        "type": "BFS",
        "step_num": 1,
    })

    while queue:
        current = queue.pop(0)

        if current not in visited:
            visited.append(current)

        steps.append({
            "current": current,
            "current_neighbor": None,
            "visited": list(visited),
            "discovered": list(discovered),
            "queue": list(queue),
            "traversed_edges": list(traversed_edges),
            "type": "BFS",
            "step_num": len(steps) + 1,
        })

        neighbors = sorted(list(graph.neighbors(current)))

        for neighbor in neighbors:
            if neighbor not in discovered:

                discovered.append(neighbor)
                queue.append(neighbor)

                traversed_edges.append((current, neighbor))

                steps.append({
                    "current": current,
                    "current_neighbor": neighbor,
                    "visited": list(visited),
                    "discovered": list(discovered),
                    "queue": list(queue),
                    "traversed_edges": list(traversed_edges),
                    "type": "BFS",
                    "step_num": len(steps) + 1,
                })

    return steps



def dfs_steps(graph, start):
    if start not in graph.nodes:
        return []

    visited = []
    finished = []
    stack = [start]
    discovered = [start]
    traversed_edges = []

    steps = []

    while stack:
        current = stack[-1]

        if current not in visited:
            visited.append(current)

            steps.append({
                "current": current,
                "current_neighbor": None,
                "visited": list(visited),
                "discovered": list(discovered),
                "finished": list(finished),
                "queue": list(stack),
                "traversed_edges": list(traversed_edges),
                "type": "DFS",
                "step_num": len(steps) + 1,
            })

        neighbors = sorted(list(graph.neighbors(current)))
        found_unvisited = False

        for neighbor in neighbors:
            if neighbor not in visited:

                traversed_edges.append((current, neighbor))

                steps.append({
                    "current": current,
                    "current_neighbor": neighbor,
                    "visited": list(visited),
                    "discovered": list(discovered),
                    "finished": list(finished),
                    "queue": list(stack),
                    "traversed_edges": list(traversed_edges),
                    "type": "DFS",
                    "step_num": len(steps) + 1,
                })

                if neighbor not in discovered:
                    discovered.append(neighbor)

                stack.append(neighbor)
                found_unvisited = True
                break

        if not found_unvisited:
            stack.pop()
            finished.append(current)

            if stack:
                steps.append({
                    "current": stack[-1],
                    "current_neighbor": None,
                    "visited": list(visited),
                    "discovered": list(discovered),
                    "finished": list(finished),
                    "queue": list(stack),
                    "traversed_edges": list(traversed_edges),
                    "type": "DFS",
                    "step_num": len(steps) + 1,
                })

    return steps




def max_flow_steps(graph, source, sink):
    """
    Ford-Fulkerson com Edmonds-Karp (BFS).
    Gera passos RICOS e DETALHADOS para visualização pedagógica completa.

    A BFS é executada SOBRE O GRAFO RESIDUAL — não sobre o grafo original.
    Cada operação interna da BFS gera um step separado para animação.
    """

    if source not in graph.nodes or sink not in graph.nodes:
        return []

    nodes = list(graph.nodes)


    capacity = {}

    for u, v, data in graph.edges(data=True):
        w = data.get("weight", 1)
        capacity[(u, v)] = w
        if (v, u) not in capacity:
            capacity[(v, u)] = 0

    flow = {edge: 0 for edge in capacity}

    steps = []
    max_flow_val = 0
    iteration = 0


    edge_lines = []
    for (u, v), cap in capacity.items():
        if cap > 0:
            edge_lines.append(f"  {u}→{v}: capacidade = {cap}, fluxo = 0")

    steps.append({
        "type": "MAX_FLOW",
        "phase": "init",
        "current": source,
        "neighbor": None,
        "visited": [],
        "queue": [source],
        "current_path": [],
        "path_edges": [],
        "flow_updates": [],
        "current_flow": 0,
        "max_flow": 0,
        "flow_on_edges": dict(flow),
        "capacity": dict(capacity),
        "iteration": iteration,
        "parent": {},
        "residual": None,
        "bottleneck": None,
        "message": (
            f"Iniciando Ford-Fulkerson (Edmonds-Karp).\n"
            f"Fonte = {source}   Sorvedouro = {sink}\n\n"
            f"Todas as arestas começam com fluxo 0.\n"
            f"A BFS será executada no GRAFO RESIDUAL a cada iteração.\n\n"
            f"Arestas e capacidades:\n"
            + "\n".join(edge_lines)
        ),
    })


    while True:

        iteration += 1

      
        bfs_visited = {source}          
        bfs_visited_list = [source]     
        bfs_parent = {source: None}     
        bfs_queue = deque([source])     
        bfs_queue_display = [source]    
        sink_found = False

        steps.append({
            "type": "MAX_FLOW",
            "phase": "bfs_start",
            "current": source,
            "neighbor": None,
            "visited": list(bfs_visited_list),
            "queue": list(bfs_queue_display),
            "current_path": [],
            "path_edges": [],
            "flow_updates": [],
            "current_flow": 0,
            "max_flow": max_flow_val,
            "flow_on_edges": dict(flow),
            "capacity": dict(capacity),
            "iteration": iteration,
            "parent": {k: v for k, v in bfs_parent.items() if v is not None},
            "residual": None,
            "bottleneck": None,
            "message": (
                f"Iteração {iteration} — Iniciando BFS no grafo residual.\n\n"
                f"A BFS percorre apenas arestas com residual > 0.\n"
                f"Residual = capacidade − fluxo atual.\n\n"
                f"Fila inicial: [{source}]\n"
                f"Objetivo: encontrar caminho de {source} até {sink}."
            ),
        })

        while bfs_queue:
            u = bfs_queue.popleft()
            bfs_queue_display = list(bfs_queue) 

           
            steps.append({
                "type": "MAX_FLOW",
                "phase": "bfs_visit_node",
                "current": u,
                "neighbor": None,
                "visited": list(bfs_visited_list),
                "queue": list(bfs_queue_display),
                "current_path": [],
                "path_edges": [],
                "flow_updates": [],
                "current_flow": 0,
                "max_flow": max_flow_val,
                "flow_on_edges": dict(flow),
                "capacity": dict(capacity),
                "iteration": iteration,
                "parent": {k: v for k, v in bfs_parent.items() if v is not None},
                "residual": None,
                "bottleneck": None,
                "message": (
                    f"Iteração {iteration} — BFS: processando nó '{u}'.\n\n"
                    f"Fila atual: {list(bfs_queue_display) if bfs_queue_display else ['vazia']}\n"
                    f"Visitados: {bfs_visited_list}\n\n"
                    f"Vamos examinar todos os vizinhos de '{u}' no grafo residual."
                ),
            })

            for v in nodes:

                cap_uv = capacity.get((u, v), 0)
                flow_uv = flow.get((u, v), 0)
                residual_uv = cap_uv - flow_uv

                if v == u:
                    continue  

                if residual_uv <= 0:
              
                    if cap_uv > 0:
                        steps.append({
                            "type": "MAX_FLOW",
                            "phase": "bfs_skip_edge",
                            "current": u,
                            "neighbor": v,
                            "visited": list(bfs_visited_list),
                            "queue": list(bfs_queue_display),
                            "current_path": [],
                            "path_edges": [],
                            "flow_updates": [],
                            "current_flow": 0,
                            "max_flow": max_flow_val,
                            "flow_on_edges": dict(flow),
                            "capacity": dict(capacity),
                            "iteration": iteration,
                            "parent": {k: v2 for k, v2 in bfs_parent.items() if v2 is not None},
                            "residual": residual_uv,
                            "bottleneck": None,
                            "message": (
                                f"Iteração {iteration} — BFS: ignorando aresta {u}→{v}.\n\n"
                                f"Capacidade original: {cap_uv}\n"
                                f"Fluxo atual:        {flow_uv}\n"
                                f"Residual:           {residual_uv}  ← zero ou negativo\n\n"
                                f"Esta aresta está SATURADA no grafo residual.\n"
                                f"Não é possível enviar mais fluxo por {u}→{v}."
                            ),
                        })
                    continue

             

                if v in bfs_visited:
                 
                    steps.append({
                        "type": "MAX_FLOW",
                        "phase": "bfs_check_edge",
                        "current": u,
                        "neighbor": v,
                        "visited": list(bfs_visited_list),
                        "queue": list(bfs_queue_display),
                        "current_path": [],
                        "path_edges": [],
                        "flow_updates": [],
                        "current_flow": 0,
                        "max_flow": max_flow_val,
                        "flow_on_edges": dict(flow),
                        "capacity": dict(capacity),
                        "iteration": iteration,
                        "parent": {k: v2 for k, v2 in bfs_parent.items() if v2 is not None},
                        "residual": residual_uv,
                        "bottleneck": None,
                        "message": (
                            f"Iteração {iteration} — BFS: aresta {u}→{v} tem residual {residual_uv}.\n\n"
                            f"Capacidade original: {cap_uv}\n"
                            f"Fluxo atual:        {flow_uv}\n"
                            f"Residual:           {cap_uv} − {flow_uv} = {residual_uv}\n\n"
                            f"Mas '{v}' já foi visitado pela BFS.\n"
                            f"Ignorando para evitar ciclos."
                        ),
                    })
                    continue

                
                bfs_visited.add(v)
                bfs_visited_list.append(v)
                bfs_parent[v] = u
                bfs_queue.append(v)
                bfs_queue_display = list(bfs_queue)

             
                is_reverse = (capacity.get((u, v), 0) == 0 and
                              capacity.get((v, u), 0) > 0)

                if is_reverse:
                    reverse_msg = (
                        f"\nEsta é uma ARESTA REVERSA {u}→{v}.\n"
                        f"A aresta original é {v}→{u} com capacidade {capacity.get((v,u),0)}.\n"
                        f"O fluxo em {v}→{u} é {flow.get((v,u),0)}, "
                        f"então a reversa {u}→{v} tem residual {residual_uv}.\n"
                        f"Usar esta aresta significa CANCELAR {residual_uv} unidades "
                        f"de fluxo enviadas por {v}→{u}."
                    )
                else:
                    reverse_msg = ""

                steps.append({
                    "type": "MAX_FLOW",
                    "phase": "bfs_enqueue",
                    "current": u,
                    "neighbor": v,
                    "visited": list(bfs_visited_list),
                    "queue": list(bfs_queue_display),
                    "current_path": [],
                    "path_edges": [],
                    "flow_updates": [],
                    "current_flow": 0,
                    "max_flow": max_flow_val,
                    "flow_on_edges": dict(flow),
                    "capacity": dict(capacity),
                    "iteration": iteration,
                    "parent": {k: v2 for k, v2 in bfs_parent.items() if v2 is not None},
                    "residual": residual_uv,
                    "bottleneck": None,
                    "message": (
                        f"Iteração {iteration} — BFS: aresta {u}→{v} é válida!\n\n"
                        f"Capacidade original: {cap_uv}\n"
                        f"Fluxo atual:        {flow_uv}\n"
                        f"Residual:           {cap_uv} − {flow_uv} = {residual_uv}  ✓\n\n"
                        f"'{v}' adicionado à fila.\n"
                        f"parent[{v}] = {u}\n"
                        f"Fila agora: {list(bfs_queue_display)}"
                        + reverse_msg
                    ),
                })

                if v == sink:
                    sink_found = True

                    steps.append({
                        "type": "MAX_FLOW",
                        "phase": "bfs_sink_found",
                        "current": u,
                        "neighbor": sink,
                        "visited": list(bfs_visited_list),
                        "queue": list(bfs_queue_display),
                        "current_path": [],
                        "path_edges": [],
                        "flow_updates": [],
                        "current_flow": 0,
                        "max_flow": max_flow_val,
                        "flow_on_edges": dict(flow),
                        "capacity": dict(capacity),
                        "iteration": iteration,
                        "parent": {k: v2 for k, v2 in bfs_parent.items() if v2 is not None},
                        "residual": residual_uv,
                        "bottleneck": None,
                        "message": (
                            f"Iteração {iteration} — BFS: SORVEDOURO '{sink}' ENCONTRADO!\n\n"
                            f"Chegamos ao destino através da aresta {u}→{sink}.\n"
                            f"Residual desta aresta: {residual_uv}\n\n"
                            f"Encerrando BFS — caminho aumentante existe.\n"
                            f"Vamos reconstruir o caminho usando o mapa de pais."
                        ),
                    })

            if sink_found:
                break  


        if sink not in bfs_parent:
           
            steps.append({
                "type": "MAX_FLOW",
                "phase": "done",
                "current": sink,
                "neighbor": None,
                "visited": list(bfs_visited_list),
                "queue": [],
                "current_path": [],
                "path_edges": [],
                "flow_updates": [],
                "current_flow": 0,
                "max_flow": max_flow_val,
                "flow_on_edges": dict(flow),
                "capacity": dict(capacity),
                "iteration": iteration,
                "parent": {},
                "residual": None,
                "bottleneck": None,
                "message": (
                    f"Iteração {iteration} — BFS concluída.\n\n"
                    f"O sorvedouro '{sink}' NÃO foi alcançado.\n"
                    f"Nós visitados pela BFS: {bfs_visited_list}\n\n"
                    f"Não existe mais nenhum caminho com capacidade residual > 0 "
                    f"de '{source}' até '{sink}'.\n\n"
                    f"O algoritmo termina aqui.\n\n"
                    f"══════════════════════════\n"
                    f"FLUXO MÁXIMO = {max_flow_val}\n"
                    f"══════════════════════════"
                ),
            })
            break  

        path = []
        v = sink
        while v is not None:
            path.append(v)
            v = bfs_parent[v]
        path.reverse()

        path_edges = [(path[i], path[i + 1]) for i in range(len(path) - 1)]

        bottleneck = float("inf")
        residual_details = []

        for u, v in path_edges:
            res = capacity.get((u, v), 0) - flow.get((u, v), 0)
            residual_details.append((u, v, res))
            bottleneck = min(bottleneck, res)


        res_lines = []
        for u, v, res in residual_details:
            marker = "  ← GARGALO" if res == bottleneck else ""
            res_lines.append(f"  {u}→{v}: residual = {res}{marker}")

  
        steps.append({
            "type": "MAX_FLOW",
            "phase": "path_found",
            "current": sink,
            "neighbor": None,
            "visited": list(bfs_visited_list),
            "queue": [],
            "current_path": list(path),
            "path_edges": list(path_edges),
            "flow_updates": [],
            "current_flow": bottleneck,
            "max_flow": max_flow_val,
            "flow_on_edges": dict(flow),
            "capacity": dict(capacity),
            "iteration": iteration,
            "parent": {k: v2 for k, v2 in bfs_parent.items() if v2 is not None},
            "residual": None,
            "bottleneck": bottleneck,
            "message": (
                f"Iteração {iteration} — Caminho aumentante encontrado!\n\n"
                f"Caminho: {' → '.join(path)}\n\n"
                f"Capacidades residuais de cada aresta:\n"
                + "\n".join(res_lines)
                + f"\n\nGargalo = {bottleneck}\n"
                f"(menor residual do caminho)\n\n"
                f"Vamos enviar {bottleneck} unidades de fluxo por este caminho."
            ),
        })


        flow_updates = []
        update_messages = []
        saturated_edges = []

        for u, v in path_edges:
            old_flow_uv = flow[(u, v)]
            old_flow_vu = flow[(v, u)]

            flow[(u, v)] += bottleneck
            flow[(v, u)] -= bottleneck

            new_flow_uv = flow[(u, v)]
            new_flow_vu = flow[(v, u)]
            cap_uv = capacity[(u, v)]
            cap_vu = capacity.get((v, u), 0)

            is_saturated = (new_flow_uv >= cap_uv)

            flow_updates.append((u, v, new_flow_uv, cap_uv))

            sat_marker = "  ⬛ SATURADA" if is_saturated else ""
            update_messages.append(
                f"  {u}→{v}: {old_flow_uv} + {bottleneck} = {new_flow_uv}/{cap_uv}{sat_marker}"
            )

            new_residual_vu = cap_vu - new_flow_vu
            update_messages.append(
                f"  {v}→{u} (reversa): residual = {cap_vu} − ({new_flow_vu}) = {new_residual_vu}"
                f"  [permite cancelar até {new_residual_vu} unidades]"
            )

            if is_saturated:
                saturated_edges.append((u, v))

        max_flow_val += bottleneck

        steps.append({
            "type": "MAX_FLOW",
            "phase": "flow_update",
            "current": sink,
            "neighbor": None,
            "visited": list(bfs_visited_list),
            "queue": [],
            "current_path": list(path),
            "path_edges": list(path_edges),
            "flow_updates": flow_updates,
            "current_flow": bottleneck,
            "max_flow": max_flow_val,
            "flow_on_edges": dict(flow),
            "capacity": dict(capacity),
            "iteration": iteration,
            "parent": {},
            "residual": None,
            "bottleneck": bottleneck,
            "message": (
                f"Iteração {iteration} — Enviando {bottleneck} unidades de fluxo.\n\n"
                + "\n".join(update_messages)
                + f"\n\nFluxo acumulado até agora: {max_flow_val}\n\n"
                f"As arestas reversas foram atualizadas automaticamente.\n"
                f"Elas permitem que iterações futuras 'desfaçam' fluxo se necessário."
            ),
        })


        for u, v in saturated_edges:
            cap_uv = capacity[(u, v)]
            steps.append({
                "type": "MAX_FLOW",
                "phase": "saturated_edge",
                "current": u,
                "neighbor": v,
                "visited": list(bfs_visited_list),
                "queue": [],
                "current_path": list(path),
                "path_edges": list(path_edges),
                "flow_updates": flow_updates,
                "current_flow": bottleneck,
                "max_flow": max_flow_val,
                "flow_on_edges": dict(flow),
                "capacity": dict(capacity),
                "iteration": iteration,
                "parent": {},
                "residual": 0,
                "bottleneck": bottleneck,
                "message": (
                    f"Iteração {iteration} — ARESTA SATURADA: {u}→{v}\n\n"
                    f"Fluxo atual:    {flow[(u,v)]}\n"
                    f"Capacidade:     {cap_uv}\n"
                    f"Residual:       0\n\n"
                    f"Esta aresta não pode receber mais fluxo direto.\n"
                    f"A BFS não poderá usá-la em iterações futuras\n"
                    f"(a menos que fluxo seja cancelado pela aresta reversa).\n\n"
                    f"Aresta reversa {v}→{u} agora tem residual = {cap_uv},\n"
                    f"permitindo cancelar até {cap_uv} unidades de fluxo."
                ),
            })

    return steps