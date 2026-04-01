import json
import base64
from dash import Input, Output, State, callback_context, html, no_update
from data.graph_store import graph_service, state
from algorithms.algorithms import bfs_steps, dfs_steps


def _build_info_box(info, algo_name=None, step=None, total=None):
    direction_label = "Orientado" if info["directed"] else "Não Orientado"
    weight_label = "Com Peso" if info["weighted"] else "Sem Peso"

    rows = [
        html.Div([html.Div(className="info-dot"), html.Span([html.Strong("Vértices: "), str(info["nodes"])])], className="info-row"),
        html.Div([html.Div(className="info-dot"), html.Span([html.Strong("Arestas: "), str(info["edges"])])], className="info-row"),
        html.Div([html.Div(className="info-dot"), html.Span([html.Strong("Tipo: "), direction_label])], className="info-row"),
        html.Div([html.Div(className="info-dot"), html.Span([html.Strong("Peso: "), weight_label])], className="info-row"),
    ]
    if algo_name and step is not None and total:
        rows.append(html.Div([
            html.Div(className="info-dot", style={"background": "#FFD700"}),
            html.Span([html.Strong(f"{algo_name}: "), f"Passo {step}/{total}"])
        ], className="info-row"))
    return rows


def _get_visited_sequence(steps):
    """Extrai a sequência de vértices visitados na ordem correta"""
    visited_in_order = []
    
    for step in steps:
        # Verifica se este passo marca a visita de um novo vértice
        current = step.get("current")
        if current and current not in visited_in_order:
            # Se o current ainda não foi adicionado, adiciona agora
            visited_in_order.append(current)
    
    return visited_in_order


def _format_sequence_display(sequence, algo_name):
    """Formata a sequência de visitados para exibição"""
    if not sequence:
        return []
    
    # Cria uma lista de elementos HTML para exibir a sequência
    sequence_elements = []
    for i, node in enumerate(sequence):
        sequence_elements.append(
            html.Span(node, style={
                "display": "inline-block",
                "backgroundColor": "#ff69b4",
                "color": "white",
                "padding": "6px 12px",
                "margin": "0 4px",
                "borderRadius": "25px",
                "fontWeight": "bold",
                "fontSize": "14px",
                "boxShadow": "0 2px 4px rgba(0,0,0,0.1)"
            })
        )
        if i < len(sequence) - 1:
            sequence_elements.append(
                html.Span("→", style={
                    "color": "#ff69b4",
                    "fontWeight": "bold",
                    "fontSize": "18px",
                    "margin": "0 4px"
                })
            )
    
    return sequence_elements


def _apply_algo_classes(elements, current_step):
    if not current_step:
        return elements
    current = current_step.get("current")
    current_neighbor = current_step.get("current_neighbor")
    visited = current_step.get("visited", [])
    queued = current_step.get("queue", [])

    for el in elements:
        el_id = el.get("data", {}).get("id", "")
        source = el.get("data", {}).get("source")
        target = el.get("data", {}).get("target")

        if source is None:
            # Node
            if el_id == current:
                el["classes"] = "algo-current"
            elif el_id in visited:
                el["classes"] = "algo-visited"
            elif el_id in queued:
                el["classes"] = "algo-queued"
            else:
                existing = el.get("classes", "")
                classes = " ".join(
                    c for c in existing.split() if c in ("selected-node", "selected-edge")
                )
                el["classes"] = classes
        else:
            # Edge - color the edge being explored in this step
            if current_neighbor and (
                (source == current and target == current_neighbor) or
                (target == current and source == current_neighbor)
            ):
                el["classes"] = "algo-edge-active"
            else:
                existing = el.get("classes", "")
                classes = " ".join(
                    c for c in existing.split() if c in ("selected-node", "selected-edge")
                )
                el["classes"] = classes
    return elements


def _clear_all_algo_classes(elements):
    for el in elements:
        existing = el.get("classes", "")
        classes = " ".join(
            c for c in existing.split() if c in ("selected-node", "selected-edge")
        )
        el["classes"] = classes
    return elements


def _export_graph():
    info = graph_service.get_info()
    lines = [f"{info['nodes']} {info['edges']}"]
    
    for u, v, data in graph_service.graph.edges(data=True):
        w = data.get("weight", 1)
        if info["weighted"]:
            lines.append(f"{u} {v} {w}")
        else:
            lines.append(f"{u} {v}")
    
    return "\n".join(lines)


def _import_graph(content, directed, weighted):
    try:
        if ',' in content:
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string).decode('utf-8')
        else:
            decoded = content
        
        lines = [line.strip() for line in decoded.split("\n") if line.strip()]
        if not lines:
            return False
        
        first_line = lines[0].split()
        if len(first_line) != 2:
            return False
        
        n_nodes, n_edges = int(first_line[0]), int(first_line[1])
        
        graph_service.clear_graph()
        graph_service.set_type(directed == "directed", weighted == "weighted")
        
        import random
        nodes_created = []
        for i in range(n_nodes):
            if i < 26:
                node_id = chr(65 + i)
            else:
                node_id = f"N{i}"
            pos_x = random.randint(100, 800)
            pos_y = random.randint(100, 500)
            graph_service.add_node(pos_x, pos_y, node_id)
            nodes_created.append(node_id)
        
        for i in range(1, len(lines)):
            line = lines[i]
            if not line:
                continue
            edge_parts = line.split()
            if len(edge_parts) >= 2:
                u, v = edge_parts[0], edge_parts[1]
                w = int(edge_parts[2]) if len(edge_parts) >= 3 and weighted else 1
                if u in nodes_created and v in nodes_created:
                    graph_service.add_edge(u, v, w)
        
        return True
    except Exception as e:
        print(f"Error importing graph: {e}")
        return False


def register_callbacks(app):
    @app.callback(
        Output("graph", "elements"),
        Output("graph", "stylesheet"),
        Output("graph", "zoom"),
        Output("graph", "pan"),
        Output("graph-direction", "value"),
        Output("graph-weight", "value"),
        Output("graph-info", "children"),
        Output("algo-status", "children"),
        Output("algo-legend", "className"),
        Output("algo-interval", "disabled"),
        Output("download-file", "data"),
        Output("run-bfs", "className"),
        Output("run-dfs", "className"),
        Output("graph-direction", "className"),
        Output("graph-weight", "className"),
        Output("next-step", "disabled"),
        Output("run-all", "disabled"),

        Input("add-node", "n_clicks"),
        Input("hidden-add-node", "n_clicks"),
        Input("hidden-add-node-at-pos", "n_clicks"),
        Input("add-edge", "n_clicks"),
        Input("hidden-delete", "n_clicks"),
        Input("btn-clear", "n_clicks"),
        Input("graph-direction", "value"),
        Input("graph-weight", "value"),
        Input("graph", "tapNodeData"),
        Input("graph", "tapEdgeData"),
        Input("run-bfs", "n_clicks"),
        Input("run-dfs", "n_clicks"),
        Input("next-step", "n_clicks"),
        Input("run-all", "n_clicks"),
        Input("update-edge-weight", "n_clicks"),
        Input("algo-interval", "n_intervals"),
        Input("download-btn", "n_clicks"),
        Input("upload", "contents"),

        State("edge-source", "value"),
        State("edge-target", "value"),
        State("edit-edge-weight", "value"),
        State("graph", "elements"),
        State("graph", "zoom"),
        State("graph", "pan"),
        State("hidden-click-position-string", "value"),
        State("algo-start", "value"),
        State("upload", "filename"),

        prevent_initial_call=True
    )
    def update_graph(
        add_node, hidden_add_node, hidden_add_node_at_pos,
        add_edge, hidden_delete, btn_clear,
        direction, weight,
        tap_node, tap_edge,
        run_bfs, run_dfs, next_step, run_all, update_edge_weight,
        algo_interval,
        download_btn, upload_content,
        edge_source, edge_target,
        edit_weight,
        elements_state, zoom, pan, click_pos, algo_start,
        upload_filename
    ):
        ctx = callback_context
        trigger = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        
        download_data = None
        bfs_class = "btn-algo"
        dfs_class = "btn-algo"
        direction_class = "radio-group"
        weight_class = "radio-group"
        next_step_disabled = False
        run_all_disabled = False

        zoom = zoom if isinstance(zoom, (int, float)) else 1
        pan = pan if isinstance(pan, dict) else {"x": 0, "y": 0}

        graph_service.update_positions_from_elements(elements_state)

        if click_pos:
            try:
                x, y = map(float, click_pos.split(","))
                state["last_position"] = {"x": x, "y": y}
            except Exception:
                pass

        show_completion_message = False
        completed_algo_name = None
        completed_sequence = None
        force_clear_classes = False
        is_completion_step = False

        
        if "download-btn" in trigger:
            content = _export_graph()
            download_data = dict(content=content, filename="graph.txt")

 
        elif "upload" in trigger and upload_content:
            if _import_graph(upload_content, direction, weight):
                state["algo_steps"] = []
                state["algo_index"] = 0
                state["auto_running"] = False
                state["selected_node"] = None
                state["selected_edge"] = None
                state["running_algo"] = None
                state["visited_sequence"] = None
                force_clear_classes = True

   
        elif "add-node" in trigger or "hidden-add-node" in trigger:
            pos = state["last_position"]
            graph_service.add_node(pos["x"], pos["y"])
            state["algo_steps"] = []
            state["algo_index"] = 0
            state["auto_running"] = False
            state["running_algo"] = None
            state["visited_sequence"] = None
            force_clear_classes = True

   
        elif "btn-clear" in trigger:
            graph_service.clear_graph()
            state["selected_node"] = None
            state["selected_edge"] = None
            state["algo_steps"] = []
            state["algo_index"] = 0
            state["auto_running"] = False
            state["running_algo"] = None
            state["visited_sequence"] = None
            force_clear_classes = True

       
        elif "add-edge" in trigger:
            if edge_source and edge_target:
                graph_service.add_edge(
                    edge_source.strip().upper(),
                    edge_target.strip().upper(),
                    1
                )
                force_clear_classes = True

        
        elif "graph.tapNodeData" in trigger and tap_node:
            node_id = tap_node["id"]
            if state["selected_node"] is None:
                state["selected_edge"] = None
                state["selected_node"] = node_id
            else:
                if state["selected_node"] != node_id:
                    graph_service.add_edge(
                        state["selected_node"], node_id, 1
                    )
                state["selected_node"] = None
                force_clear_classes = True

  
        elif "graph.tapEdgeData" in trigger and tap_edge:
            edge_id = tap_edge["id"]
            if state["selected_edge"] == edge_id:
                state["selected_edge"] = None
            else:
                state["selected_node"] = None
                state["selected_edge"] = edge_id

  
        elif "hidden-delete" in trigger:
            if state["selected_node"]:
                graph_service.remove_node(state["selected_node"])
                state["selected_node"] = None
                state["algo_steps"] = []
                state["algo_index"] = 0
                state["auto_running"] = False
                state["running_algo"] = None
                state["visited_sequence"] = None
                force_clear_classes = True
            elif state["selected_edge"]:
                edge_id = state["selected_edge"]
                parts = edge_id.split("-")
                if len(parts) >= 3:
                    u = parts[1]
                    v = "-".join(parts[2:]) if len(parts) > 3 else parts[2]
                    
                    graph_service.edges_data = [
                        (a, b, w) for (a, b, w) in graph_service.edges_data
                        if not ((a == u and b == v) or (not graph_service.directed and a == v and b == u))
                    ]
                    graph_service._rebuild_graph()
                state["selected_edge"] = None
                force_clear_classes = True

        
        elif "update-edge-weight" in trigger:
            if state["selected_edge"] and edit_weight is not None:
                parts = state["selected_edge"].split("-")
                if len(parts) >= 3:
                    u = parts[1]
                    v = "-".join(parts[2:]) if len(parts) > 3 else parts[2]
                    
                    graph_service.edges_data = [
                        (a, b, int(edit_weight)) if ((a == u and b == v) or (not graph_service.directed and a == v and b == u)) else (a, b, w)
                        for (a, b, w) in graph_service.edges_data
                    ]
                    graph_service._rebuild_graph()
                    force_clear_classes = True

      
        elif "run-bfs" in trigger:
            if algo_start and algo_start.strip().upper() in graph_service.graph.nodes:
                state["algo_steps"] = bfs_steps(graph_service.graph, algo_start.strip().upper())
                state["algo_index"] = 0
                state["running_algo"] = "BFS"
                state["auto_running"] = False
                state["visited_sequence"] = None
                bfs_class = "btn-algo btn-algo-active"
                dfs_class = "btn-algo"
                force_clear_classes = False


        elif "run-dfs" in trigger:
            if algo_start and algo_start.strip().upper() in graph_service.graph.nodes:
                state["algo_steps"] = dfs_steps(graph_service.graph, algo_start.strip().upper())
                state["algo_index"] = 0
                state["running_algo"] = "DFS"
                state["auto_running"] = False
                state["visited_sequence"] = None
                dfs_class = "btn-algo btn-algo-active"
                bfs_class = "btn-algo"
                force_clear_classes = False

   
        elif "next-step" in trigger:
            if state["algo_steps"] and state["algo_index"] < len(state["algo_steps"]):
                if state["algo_index"] < len(state["algo_steps"]) - 1:
                    state["algo_index"] += 1
                elif state["algo_index"] == len(state["algo_steps"]) - 1:
                    is_completion_step = True

      
        elif "run-all" in trigger:
            if state["algo_steps"]:
                state["auto_running"] = True


       
        elif "algo-interval" in trigger and state["auto_running"] and state["algo_steps"]:
            if state["algo_index"] < len(state["algo_steps"]) - 1:
                state["algo_index"] += 1
            elif state["algo_index"] == len(state["algo_steps"]) - 1:
                is_completion_step = True
                state["auto_running"] = False

      
        elif "graph-direction" in trigger or "graph-weight" in trigger:
            state["algo_steps"] = []
            state["algo_index"] = 0
            state["running_algo"] = None
            state["auto_running"] = False
            state["visited_sequence"] = None
            force_clear_classes = True

        graph_service.set_type(direction == "directed", weight == "weighted")
        
   
        elements = graph_service.get_elements()

   
        for el in elements:
            el_id = el.get("data", {}).get("id", "")
            is_edge = "source" in el.get("data", {})
            if not is_edge and el_id == state["selected_node"]:
                el["classes"] = "selected-node"
            elif is_edge and el_id == state["selected_edge"]:
                el["classes"] = "selected-edge"


        current_step = None
        algo_finished = False
        total_steps = len(state["algo_steps"])
        
        if force_clear_classes:
            elements = _clear_all_algo_classes(elements)
        elif state["algo_steps"] and total_steps > 0:
            if state["algo_index"] < total_steps:
                current_step = state["algo_steps"][state["algo_index"]]
                elements = _apply_algo_classes(elements, current_step)
                
                if state["algo_index"] == total_steps - 1 and is_completion_step:
                    algo_finished = True
                    completed_algo_name = state.get("running_algo", "Algoritmo")
                    # Extrai a sequência de visitados quando o algoritmo termina
                    completed_sequence = _get_visited_sequence(state["algo_steps"])
                    state["visited_sequence"] = completed_sequence
                    state["_pending_completion"] = True
            elif state["algo_index"] >= total_steps:
                algo_finished = True
                completed_algo_name = state.get("running_algo", "Algoritmo")
                completed_sequence = state.get("visited_sequence", [])
                elements = _clear_all_algo_classes(elements)


        if algo_finished and state.get("_pending_completion"):
            state["algo_steps"] = []
            state["algo_index"] = 0
            state["running_algo"] = None
            state["auto_running"] = False
            state["_pending_completion"] = False
            bfs_class = "btn-algo"
            dfs_class = "btn-algo"
            next_step_disabled = False
            run_all_disabled = False
            elements = _clear_all_algo_classes(elements)
        elif not state["algo_steps"]:
            next_step_disabled = True
            run_all_disabled = True
        elif state["algo_index"] >= total_steps - 1:
            run_all_disabled = True
            next_step_disabled = False
        else:
            next_step_disabled = False
            run_all_disabled = False


        arrow_shape = "triangle" if direction == "directed" else "none"
        stylesheet = [
            {
                "selector": "node",
                "style": {
                    "background-color": "#ff69b4",
                    "label": "data(label)",
                    "color": "white",
                    "font-size": "14px",
                    "font-weight": "bold",
                    "width": 40,
                    "height": 40,
                    "text-valign": "center",
                    "text-halign": "center",
                    "text-outline-width": 2,
                    "text-outline-color": "#c2185b",
                    "border-width": 2,
                    "border-color": "#c2185b",
                }
            },
            {
                "selector": "edge",
                "style": {
                    "line-color": "#ff1493",
                    "target-arrow-color": "#ff1493",
                    "target-arrow-shape": arrow_shape,
                    "curve-style": "bezier",
                    "width": 2.5,
                    "label": "data(label)",
                    "font-size": "13px",
                    "font-weight": "bold",
                    "color": "#8B004B",
                    "text-background-color": "#fff0f6",
                    "text-background-opacity": 1,
                    "text-background-padding": "4px",
                    "text-background-shape": "roundrectangle",
                    "text-border-opacity": 1,
                    "text-border-width": 1.5,
                    "text-border-color": "#ff69b4",
                    "text-rotation": "autorotate",
                }
            },
            {
                "selector": ".selected-node",
                "style": {
                    "background-color": "#ff00cc",
                    "border-width": 4,
                    "border-color": "#8B004B",
                }
            },
            {
                "selector": ".selected-edge",
                "style": {
                    "line-color": "#8B004B",
                    "target-arrow-color": "#8B004B",
                    "width": 4,
                }
            },
            {
                "selector": ".algo-current",
                "style": {
                    "background-color": "#FFD700",
                    "border-color": "#b8860b",
                    "border-width": 3,
                    "color": "#3d2000",
                    "text-outline-color": "#FFD700",
                    "width": 46,
                    "height": 46,
                }
            },
            {
                "selector": ".algo-visited",
                "style": {
                    "background-color": "#87CEFA",
                    "border-color": "#4682b4",
                    "border-width": 2,
                    "color": "#003060",
                    "text-outline-color": "#87CEFA",
                }
            },
            {
                "selector": ".algo-queued",
                "style": {
                    "background-color": "#b0f0c0",
                    "border-color": "#2e8b57",
                    "border-width": 2,
                    "color": "#003020",
                    "text-outline-color": "#b0f0c0",
                }
            },
            {
                "selector": ".algo-edge-active",
                "style": {
                    "line-color": "#FFD700",
                    "target-arrow-color": "#FFD700",
                    "width": 4,
                }
            },
        ]

        info = graph_service.get_info()
        step_num = state["algo_index"] + 1 if state["algo_steps"] and state["algo_index"] < total_steps else None

        show_algo_name = state.get("running_algo") if state["algo_steps"] and not algo_finished else None
        
        info_children = _build_info_box(
            info,
            algo_name=show_algo_name,
            step=step_num,
            total=total_steps if total_steps else None
        )

        if algo_finished and completed_algo_name and completed_sequence:
            # Formata a sequência de visitados para exibição
            sequence_display = _format_sequence_display(completed_sequence, completed_algo_name)
            
            # Converte a sequência para string para fácil visualização
            sequence_string = " → ".join(completed_sequence)
            
            algo_status = [
                html.Div(f"{completed_algo_name} — Concluído!", 
                        style={"fontWeight": "700", "marginBottom": "12px", "color": "#8B004B", "fontSize": "16px"}),
                html.Div("Sequência de vértices visitados:", 
                        style={"fontWeight": "600", "marginBottom": "10px", "color": "#ff69b4", "fontSize": "13px"}),
                html.Div(sequence_display, 
                        style={"marginBottom": "12px", "padding": "12px", "backgroundColor": "#fff0f6", 
                               "borderRadius": "10px", "border": "2px solid #ff69b4", "textAlign": "center"}),
                html.Div(f"Total de vértices visitados: {len(completed_sequence)}", 
                        style={"color": "#2e8b57", "fontSize": "12px", "marginTop": "8px", "fontWeight": "500"}),
                html.Div("✓ Algoritmo finalizado! Você pode executar um novo algoritmo quando desejar.", 
                        style={"color": "#ff69b4", "fontSize": "11px", "marginTop": "8px", "fontStyle": "italic"})
            ]
        elif current_step:
            algo_name = state.get("running_algo", "Algoritmo")
            visited_str = " → ".join(current_step["visited"])
            queue_str = ", ".join(current_step["queue"]) if current_step["queue"] else "vazia"
            queue_label = "Fila" if algo_name == "BFS" else "Pilha"
            step_idx = state["algo_index"] + 1
            
            current_neighbor = current_step.get("current_neighbor")
            edge_info = []
            if current_neighbor:
                edge_info.append(
                    html.Div(f"Explorando aresta: {current_step['current']} → {current_neighbor}", 
                            style={"color": "#FFD700", "fontSize": "11px", "marginTop": "3px", "fontWeight": "bold"})
                )
            
            algo_status = [
                html.Div(f"{algo_name} — Passo {step_idx}/{total_steps}", style={"fontWeight": "700", "marginBottom": "4px"}),
                html.Div(f"Atual: {current_step['current']}", style={"color": "#b8860b"}),
            ] + edge_info + [
                html.Div(f"Visitados: {visited_str}", style={"color": "#4682b4", "fontSize": "11px", "marginTop": "3px"}),
                html.Div(f"{queue_label}: {queue_str}", style={"color": "#2e8b57", "fontSize": "11px"}),
            ]
        else:
            algo_status = "Nenhum algoritmo rodando."


        legend_class = "algo-legend visible" if (state["algo_steps"] and not algo_finished and not force_clear_classes) else "algo-legend"

        interval_disabled = not state["auto_running"]

        return (
            elements, stylesheet, zoom, pan,
            direction, weight,
            info_children, algo_status,
            legend_class, interval_disabled,
            download_data,
            bfs_class, dfs_class,
            direction_class, weight_class,
            next_step_disabled, run_all_disabled
        )