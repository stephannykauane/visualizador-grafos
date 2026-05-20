import json
import base64
from dash import Input, Output, State, callback_context, html, no_update
from data.graph_store import graph_service, state
from algorithms.algorithms import bfs_steps, dfs_steps, max_flow_steps



def _build_info_box(info, algo_name=None, step=None, total=None):
    direction_label = "Orientado" if info["directed"] else "Não Orientado"
    weight_label = "Com Peso" if info["weighted"] else "Sem Peso"
    rows = [
        html.Div([html.Div(className="info-dot"),
                  html.Span([html.Strong("Vértices: "), str(info["nodes"])])],
                 className="info-row"),
        html.Div([html.Div(className="info-dot"),
                  html.Span([html.Strong("Arestas: "), str(info["edges"])])],
                 className="info-row"),
        html.Div([html.Div(className="info-dot"),
                  html.Span([html.Strong("Tipo: "), direction_label])],
                 className="info-row"),
        html.Div([html.Div(className="info-dot"),
                  html.Span([html.Strong("Peso: "), weight_label])],
                 className="info-row"),
    ]
    if algo_name and step is not None and total:
        rows.append(html.Div([
            html.Div(className="info-dot",
                     style={"background": "#ff1493"}),
            html.Span([html.Strong(f"{algo_name}: "),
                       f"Passo {step}/{total}"])
        ], className="info-row"))
    return rows


def _get_visited_sequence(steps):
    visited_in_order = []
    for step in steps:
        current = step.get("current")
        if current and current not in visited_in_order:
            visited_in_order.append(current)
    return visited_in_order


def _format_sequence_display(sequence, algo_name):
    if not sequence:
        return []
    elements = []
    for i, node in enumerate(sequence):
        elements.append(
            html.Span(node, style={
                "display": "inline-block",
                "backgroundColor": "#ff1493",
                "color": "white",
                "padding": "4px 10px",
                "margin": "0 2px",
                "borderRadius": "20px",
                "fontWeight": "bold",
                "fontSize": "13px",
            })
        )
        if i < len(sequence) - 1:
            elements.append(html.Span("→", style={
                "color": "#ff1493", "fontWeight": "bold",
                "fontSize": "15px", "margin": "0 2px"
            }))
    return elements



_KEEP_CLASSES = {"selected-node", "selected-edge"}
_ALL_ALGO_CLASSES = {
    "algo-current", "algo-discovered", "algo-visited", "algo-finished",
    "algo-edge-active",
    "maxflow-path", "maxflow-node", "maxflow-source", "maxflow-sink",
    "maxflow-residual", "maxflow-dimmed", "maxflow-bfs-visited",
    "maxflow-bfs-current", "maxflow-bfs-neighbor-valid",
    "maxflow-bfs-neighbor-skip",
}


def _clear_algo_classes(elements):
    for el in elements:
        existing = el.get("classes", "")
        kept = " ".join(c for c in existing.split() if c in _KEEP_CLASSES)
        el["classes"] = kept
    return elements




def _apply_bfs_dfs_classes(elements, step):
    if not step:
        return elements

    current = step.get("current")
    current_neighbor = step.get("current_neighbor")

    visited = set(step.get("visited", []))
    discovered = set(step.get("discovered", []))
    finished = set(step.get("finished", []))

    traversed_edges = set(
        tuple(edge) for edge in step.get("traversed_edges", [])
    )

    algo_type = step.get("type", "BFS")

    for el in elements:
        data = el.get("data", {})
        el_id = data.get("id", "")
        is_edge = "source" in data

        if is_edge:
            src = data["source"]
            tgt = data["target"]

            is_current_edge = (
                current_neighbor and (
                    (src == current and tgt == current_neighbor) or
                    (tgt == current and src == current_neighbor)
                )
            )

            is_traversed = (
                (src, tgt) in traversed_edges or
                (tgt, src) in traversed_edges
            )

            if is_current_edge:
                el["classes"] = "algo-edge-active"

            elif is_traversed:
                el["classes"] = "algo-edge-visited"

            else:
                existing = el.get("classes", "")
                el["classes"] = " ".join(
                    c for c in existing.split()
                    if c in _KEEP_CLASSES
                )

        else:
            if el_id == current:
                el["classes"] = "algo-current"

            elif algo_type == "DFS" and el_id in finished:
                el["classes"] = "algo-finished"

            elif el_id in visited:
                el["classes"] = "algo-visited"

            elif el_id in discovered:
                el["classes"] = "algo-discovered"

            else:
                existing = el.get("classes", "")
                el["classes"] = " ".join(
                    c for c in existing.split()
                    if c in _KEEP_CLASSES
                )

    return elements


def _apply_maxflow_classes(elements, step, source, sink):
    if not step:
        return elements

    phase = step.get("phase", "")
    path = set(step.get("current_path", []))
    path_edges = set(tuple(e) for e in step.get("path_edges", []))
    bfs_visited = set(step.get("visited", []))
    capacity = step.get("capacity", {})
    current = step.get("current")
    neighbor = step.get("neighbor")

    # Fases que mostram a BFS acontecendo
    bfs_phases = {
        "bfs_start", "bfs_visit_node", "bfs_check_edge",
        "bfs_skip_edge", "bfs_enqueue", "bfs_sink_found",
    }

    for el in elements:
        data = el.get("data", {})
        el_id = data.get("id", "")
        is_edge = "source" in data

        if is_edge:
            src, tgt = data["source"], data["target"]
            edge_fwd = (src, tgt)
            edge_rev = (tgt, src)

            if phase in ("path_found", "flow_update", "saturated_edge"):
                if edge_fwd in path_edges:
                    el["classes"] = "maxflow-path"
                elif edge_rev in path_edges and capacity.get(edge_fwd, 0) == 0:
                    el["classes"] = "maxflow-residual"
                else:
                    el["classes"] = "maxflow-dimmed"

            elif phase in bfs_phases:
                # Durante a BFS: destacar aresta sendo analisada
                is_current_edge = (
                    neighbor and (
                        (src == current and tgt == neighbor) or
                        (tgt == current and src == neighbor)
                    )
                )
                if is_current_edge:
                    if phase == "bfs_enqueue" or phase == "bfs_sink_found":
                        el["classes"] = "maxflow-path"       # válida dourado
                    elif phase == "bfs_skip_edge":
                        el["classes"] = "maxflow-dimmed"     # inválida desbotada
                    else:
                        el["classes"] = "maxflow-residual"   # sendo verificada azul
                else:
                    existing = el.get("classes", "")
                    el["classes"] = " ".join(
                        c for c in existing.split() if c in _KEEP_CLASSES)

            elif phase == "done":
                if capacity.get(edge_fwd, 0) > 0:
                    flow_val = step.get("flow_on_edges", {}).get(edge_fwd, 0)
                    if flow_val > 0:
                        el["classes"] = "maxflow-residual"
                    else:
                        existing = el.get("classes", "")
                        el["classes"] = " ".join(
                            c for c in existing.split() if c in _KEEP_CLASSES)
                else:
                    existing = el.get("classes", "")
                    el["classes"] = " ".join(
                        c for c in existing.split() if c in _KEEP_CLASSES)

            else:
                existing = el.get("classes", "")
                el["classes"] = " ".join(
                    c for c in existing.split() if c in _KEEP_CLASSES)

        else:
            # Nós
            if phase in ("path_found", "flow_update", "saturated_edge"):
                if el_id == source:
                    el["classes"] = "maxflow-source"
                elif el_id == sink:
                    el["classes"] = "maxflow-sink"
                elif el_id in path:
                    el["classes"] = "maxflow-node"
                else:
                    el["classes"] = "maxflow-dimmed"

            elif phase in bfs_phases:
                if el_id == source:
                    el["classes"] = "maxflow-source"
                elif el_id == sink:
                    el["classes"] = "maxflow-sink"
                elif el_id == current:
                    el["classes"] = "algo-current"          # nó atual da BFS dourado
                elif el_id == neighbor and neighbor:
                    if phase in ("bfs_enqueue", "bfs_sink_found"):
                        el["classes"] = "maxflow-node"      # vizinho válido dourado
                    else:
                        el["classes"] = "algo-discovered"   # vizinho sendo verificado  cinza
                elif el_id in bfs_visited:
                    el["classes"] = "maxflow-bfs-visited"   # já visitado  cinza escuro
                else:
                    existing = el.get("classes", "")
                    el["classes"] = " ".join(
                        c for c in existing.split() if c in _KEEP_CLASSES)

            elif phase == "done":
                if el_id == source:
                    el["classes"] = "maxflow-source"
                elif el_id == sink:
                    el["classes"] = "maxflow-sink"
                else:
                    el["classes"] = "algo-finished"

            else:
                existing = el.get("classes", "")
                el["classes"] = " ".join(
                    c for c in existing.split() if c in _KEEP_CLASSES)

    return elements

def _build_stylesheet(direction):
    arrow = "triangle" if direction == "directed" else "none"
    is_maxflow = state.get("running_algo") == "Fluxo Máximo"

    edge_font_size = "13px" if is_maxflow else "11px"
    edge_text_bg_padding = "4px" if is_maxflow else "2px"

    return [
        {
            "selector": "node",
            "style": {
                "background-color": "#FFFFFF",
                "label": "data(label)",
                "color": "#212121",
                "font-size": "14px",
                "font-weight": "bold",
                "width": 40,
                "height": 40,
                "text-valign": "center",
                "text-halign": "center",
                "text-outline-width": 1,
                "text-outline-color": "#FFFFFF",
                "border-width": 2,
                "border-color": "#212121",
                "transition-property": "background-color, border-color, opacity",
                "transition-duration": "0.25s",
            }
        },
        {
            "selector": "edge",
            "style": {
                "line-color": "#616161",
                "target-arrow-color": "#616161",
                "target-arrow-shape": arrow,
                "curve-style": "bezier",
                "width": 2.5,
                "label": "data(label)",
                "font-size": edge_font_size,
                "font-weight": "700",
                "color": "#1a1a1a",
                "text-background-color": "#FFFFFF",
                "text-background-opacity": 1,
                "text-background-padding": edge_text_bg_padding,
                "text-background-shape": "roundrectangle",
                "text-border-opacity": 1,
                "text-border-width": 1.5,
                "text-border-color": "#BDBDBD",
                "text-rotation": "autorotate",
                "transition-property": "line-color, width, opacity",
                "transition-duration": "0.25s",
            }
        },

        # Aresta saturada (fluxo == capacidade)
        {
            "selector": "[saturated = 1]",
            "style": {
                "line-color": "#b91c1c",
                "target-arrow-color": "#b91c1c",
                "width": 3.5,
                "color": "#7f1d1d",
                "text-background-color": "#fef2f2",
                "text-border-color": "#b91c1c",
                "text-border-width": 1.5,
            }
        },

        {"selector": ".selected-node",
         "style": {"background-color": "#ff69b4",
                   "border-width": 4, "border-color": "#8B004B"}},
        {"selector": ".selected-edge",
         "style": {"line-color": "#8B004B",
                   "target-arrow-color": "#8B004B", "width": 4}},

        # BFS/DFS acadêmico
        {"selector": ".algo-current",
         "style": {
             "background-color": "#FFD700", "border-color": "#b8860b",
             "border-width": 3, "color": "#1a0e00",
             "text-outline-color": "#FFD700", "width": 46, "height": 46,
         }},
        {"selector": ".algo-discovered",
         "style": {
             "background-color": "#9E9E9E", "border-color": "#616161",
             "border-width": 2, "color": "#212121",
             "text-outline-color": "#9E9E9E",
         }},
        {"selector": ".algo-visited",
         "style": {
             "background-color": "#212121", "border-color": "#000000",
             "border-width": 2, "color": "#FFFFFF",
             "text-outline-color": "#212121",
         }},
        {"selector": ".algo-finished",
         "style": {
             "background-color": "#212121", "border-color": "#000000",
             "border-width": 2, "color": "#FFFFFF",
             "text-outline-color": "#212121",
         }},
        {"selector": ".algo-edge-active",
         "style": {
             "line-color": "#FFD700", "target-arrow-color": "#FFD700",
             "target-arrow-shape": arrow, "width": 4,
         }},
        {
            "selector": ".algo-edge-visited",
            "style": {
                "line-color": "#A855F7",
                "target-arrow-color": "#A855F7",
                "target-arrow-shape": arrow,
                "width": 4,
                "opacity": 0.85,
            }
        },

        # Max Flow — caminho ativo
        {"selector": ".maxflow-path",
         "style": {
             "line-color": "#FFD700", "target-arrow-color": "#FFD700",
             "target-arrow-shape": "triangle", "width": 5,
             "font-size": "13px",
             "font-weight": "900",
             "color": "#1a0e00",
             "text-background-color": "#FEF9C3",
             "text-background-padding": "4px",
             "text-border-color": "#b8860b",
             "text-border-width": 2,
             "transition-property": "line-color, width",
             "transition-duration": "0.25s",
         }},
        {"selector": ".maxflow-node",
         "style": {
             "background-color": "#FFD700", "border-color": "#b8860b",
             "border-width": 3, "color": "#1a0e00",
             "text-outline-color": "#FFD700", "width": 46, "height": 46,
         }},
        {"selector": ".maxflow-source",
         "style": {
             "background-color": "#16a34a", "border-color": "#14532d",
             "border-width": 3, "color": "#FFFFFF",
             "text-outline-color": "#16a34a", "width": 48, "height": 48,
         }},
        {"selector": ".maxflow-sink",
         "style": {
             "background-color": "#dc2626", "border-color": "#7f1d1d",
             "border-width": 3, "color": "#FFFFFF",
             "text-outline-color": "#dc2626", "width": 48, "height": 48,
         }},
        {"selector": ".maxflow-residual",
         "style": {
             "line-color": "#3b82f6", "target-arrow-color": "#3b82f6",
             "target-arrow-shape": "triangle", "width": 2.5,
             "line-style": "dashed",
             "font-size": "12px",
             "color": "#1e3a8a",
             "text-background-color": "#eff6ff",
             "text-background-padding": "3px",
             "text-border-color": "#3b82f6",
             "text-border-width": 1,
             "transition-property": "line-color, width",
             "transition-duration": "0.25s",
         }},
        {"selector": ".maxflow-dimmed",
         "style": {
             "opacity": 0.18,
             "transition-property": "opacity",
             "transition-duration": "0.25s",
         }},
        {"selector": ".maxflow-bfs-visited",
         "style": {
             "background-color": "#9E9E9E", "border-color": "#616161",
             "border-width": 2, "color": "#212121",
             "text-outline-color": "#9E9E9E",
         }},
    ]



_PHASE_LABELS = {
    "init":             ("", "Inicialização"),
    "bfs_start":        ("", "BFS — Início"),
    "bfs_visit_node":   ("", "BFS — Visitando Nó"),
    "bfs_check_edge":   ("", "BFS — Verificando Aresta"),
    "bfs_skip_edge":    ("", "BFS — Aresta Ignorada"),
    "bfs_enqueue":      ("", "BFS — Enfileirando"),
    "bfs_sink_found":   ("", "BFS — Sorvedouro Encontrado"),
    "path_found":       ("",  "Caminho Aumentante"),
    "bottleneck":       ("", "Gargalo"),
    "flow_update":      ("", "Atualizando Fluxo"),
    "reverse_edge_update": ("", "Aresta Reversa"),
    "saturated_edge":   ("", "Aresta Saturada"),
    "done":             ("",  "Concluído"),
}




def _build_algo_status(current_step, total_steps, running_algo, algo_index):
    if not current_step:
        return "Nenhum algoritmo rodando."

    algo_type = current_step.get("type", "")
    step_idx = algo_index + 1

    if algo_type == "MAX_FLOW":
        phase = current_step.get("phase", "")
        path = current_step.get("current_path", [])
        current_flow = current_step.get("current_flow", 0)
        max_flow = current_step.get("max_flow", 0)
        flow_updates = current_step.get("flow_updates", [])
        iteration = current_step.get("iteration", 0)
        bfs_visited = current_step.get("visited", [])
        bfs_queue = current_step.get("queue", [])
        neighbor = current_step.get("neighbor")
        current_node = current_step.get("current")
        residual = current_step.get("residual")
        bottleneck = current_step.get("bottleneck")
        parent_map = current_step.get("parent", {})

        items = []

        phase_icon, phase_label = _PHASE_LABELS.get(phase, ("•", phase))
        items.append(
            html.Div(
                [
                    html.Span(phase_icon, style={"marginRight": "6px",
                                                  "fontSize": "14px"}),
                    html.Strong(phase_label,
                                style={"fontSize": "12px",
                                       "color": "#8B004B",
                                       "letterSpacing": "0.3px"}),
                    html.Span(
                        f"  iteração {iteration}",
                        style={"fontSize": "11px", "color": "#9E9E9E",
                               "marginLeft": "8px"}
                    ) if iteration else "",
                ],
                style={
                    "background": "#fff0f6",
                    "border": "1.5px solid #ffb6d9",
                    "borderRadius": "8px",
                    "padding": "5px 10px",
                    "marginBottom": "8px",
                    "display": "flex",
                    "alignItems": "center",
                }
            )
        )

  
        message = current_step.get("message")
        if message:
            items.append(
                html.Div(
                    message,
                    style={
                        "whiteSpace": "pre-line",
                        "background": "#fff7ed",
                        "border": "1px solid #fdba74",
                        "borderLeft": "4px solid #f97316",
                        "padding": "10px",
                        "borderRadius": "8px",
                        "fontSize": "12px",
                        "lineHeight": "1.6",
                        "marginBottom": "10px",
                        "color": "#7c2d12",
                        "fontWeight": "500",
                    }
                )
            )


        bfs_phases = {
            "bfs_start", "bfs_visit_node", "bfs_check_edge",
            "bfs_skip_edge", "bfs_enqueue", "bfs_sink_found",
        }

        if phase in bfs_phases:
            row_items = []

            # Nó atual da BFS
            if current_node:
                row_items.append(
                    html.Div([
                        html.Span("Nó atual: ",
                                  style={"fontWeight": "600",
                                         "color": "#616161",
                                         "fontSize": "11px"}),
                        html.Span(str(current_node),
                                  style={"fontWeight": "700",
                                         "fontSize": "13px",
                                         "color": "#1a0e00",
                                         "background": "#FEF9C3",
                                         "padding": "1px 10px",
                                         "borderRadius": "12px",
                                         "border": "1.5px solid #b8860b"}),
                    ], style={"marginBottom": "4px"})
                )

            
            if neighbor:
                row_items.append(
                    html.Div([
                        html.Span("Vizinho: ",
                                  style={"fontWeight": "600",
                                         "color": "#616161",
                                         "fontSize": "11px"}),
                        html.Span(str(neighbor),
                                  style={"fontWeight": "700",
                                         "fontSize": "13px",
                                         "color": "#1e3a8a",
                                         "background": "#eff6ff",
                                         "padding": "1px 10px",
                                         "borderRadius": "12px",
                                         "border": "1.5px solid #3b82f6"}),
                        html.Span(
                            f"  residual = {residual}"
                            if residual is not None else "",
                            style={"fontSize": "11px",
                                   "color": "#16a34a" if (residual or 0) > 0 else "#dc2626",
                                   "fontWeight": "700",
                                   "marginLeft": "6px",
                                   "fontFamily": "Space Mono, monospace"}
                        ),
                    ], style={"marginBottom": "4px"})
                )

            
            queue_str = ", ".join(str(n) for n in bfs_queue) if bfs_queue else "vazia"
            row_items.append(
                html.Div([
                    html.Span("Fila BFS: ",
                              style={"fontWeight": "600", "color": "#616161",
                                     "fontSize": "11px"}),
                    html.Span(f"[ {queue_str} ]",
                              style={"fontFamily": "Space Mono, monospace",
                                     "fontSize": "11px",
                                     "color": "#1e3a8a"}),
                ], style={"marginBottom": "4px"})
            )


            vis_str = ", ".join(str(n) for n in bfs_visited) if bfs_visited else "—"
            row_items.append(
                html.Div([
                    html.Span("Visitados: ",
                              style={"fontWeight": "600", "color": "#616161",
                                     "fontSize": "11px"}),
                    html.Span(vis_str,
                              style={"fontFamily": "Space Mono, monospace",
                                     "fontSize": "11px"}),
                ], style={"marginBottom": "4px"})
            )

            
            if parent_map:
                parent_str = "  ".join(
                    f"{k}←{v}" for k, v in parent_map.items()
                )
                row_items.append(
                    html.Div([
                        html.Span("Pais: ",
                                  style={"fontWeight": "600",
                                         "color": "#616161",
                                         "fontSize": "11px"}),
                        html.Span(parent_str,
                                  style={"fontFamily": "Space Mono, monospace",
                                         "fontSize": "11px",
                                         "color": "#7c3aed"}),
                    ], style={"marginBottom": "4px"})
                )

            items.append(
                html.Div(row_items, style={
                    "background": "#f8fafc",
                    "border": "1px solid #e2e8f0",
                    "borderRadius": "8px",
                    "padding": "8px 10px",
                    "marginBottom": "8px",
                })
            )

        
        if path:
            items.append(
                html.Span("Caminho aumentante", className="status-label")
            )
            items.append(
                html.Div(" → ".join(path), className="path-display")
            )

        
        children = []
        if current_flow and phase in ("path_found", "flow_update",
                                       "saturated_edge"):
            children.append(html.Div([
                html.Span("Gargalo", className="status-label"),
                html.Span(str(current_flow), className="status-bottleneck"),
            ]))

        children.append(html.Div([
            html.Span("Fluxo acumulado", className="status-label"),
            html.Span(str(max_flow), className="status-value-large"),
        ]))

        items.append(
            html.Div(children,
                     style={"display": "flex", "gap": "24px",
                             "marginBottom": "8px",
                             "alignItems": "flex-end"})
        )

        
        if flow_updates:
            items.append(
                html.Span("Atualizações nas arestas", className="status-label")
            )
            for u, v, f, cap in flow_updates:
                is_saturated = (f >= cap)
                saturated_style = {}
                if is_saturated:
                    saturated_style = {
                        "borderLeft": "3px solid #b91c1c",
                        "color": "#7f1d1d",
                        "background": "#fef2f2",
                        "fontWeight": "900",
                    }
                items.append(
                    html.Span(
                        [
                            f"{u} → {v}  =  ",
                            html.Strong(
                                f"{f}/{cap}",
                                style={"fontSize": "13px",
                                       "color": "#b91c1c" if is_saturated else "#16a34a"}
                            ),
                            html.Span(
                                " ⬛ SATURADA" if is_saturated else "",
                                style={"fontSize": "10px", "color": "#b91c1c",
                                       "marginLeft": "6px",
                                       "fontWeight": "700",
                                       "letterSpacing": "0.5px"}
                            ),
                        ],
                        className="flow-row",
                        style=saturated_style,
                    )
                )


        if phase in ("path_found", "flow_update", "done", "saturated_edge"):
            flow_on_edges = current_step.get("flow_on_edges", {})
            capacity_map = current_step.get("capacity", {})
            edge_rows = []
            for (src, tgt), cap in capacity_map.items():
                if cap <= 0:
                    continue
                f = max(0, flow_on_edges.get((src, tgt), 0))
                if f > 0 or phase == "done":
                    edge_rows.append((src, tgt, f, cap))

            if edge_rows:
                items.append(
                    html.Span("Estado atual das arestas",
                              className="status-label",
                              style={"marginTop": "6px", "display": "block"})
                )
                for src, tgt, f, cap in edge_rows:
                    is_sat = (f >= cap)
                    items.append(
                        html.Span(
                            [
                                f"{src}→{tgt}  ",
                                html.Strong(
                                    f"{f}/{cap}",
                                    style={"color": "#b91c1c" if is_sat
                                           else "#374151"}
                                ),
                            ],
                            className="flow-row",
                            style={"borderLeft": "3px solid #b91c1c",
                                   "background": "#fef2f2"} if is_sat else {},
                        )
                    )

        
        if phase == "init":
            flow_on_edges = current_step.get("flow_on_edges", {})
            capacity_map = current_step.get("capacity", {})
            items.append(
                html.Span("Fluxo inicial (0/capacidade)",
                          className="status-label")
            )
            for (src, tgt), cap in capacity_map.items():
                if cap <= 0:
                    continue
                items.append(
                    html.Span(f"{src}→{tgt}  0/{cap}", className="flow-row")
                )

        return items

    else:
        
        algo_name = running_algo or algo_type
        visited = current_step.get("visited", [])
        discovered = current_step.get("discovered", [])
        finished = current_step.get("finished", [])
        queue = current_step.get("queue", [])
        current = current_step.get("current")
        neighbor = current_step.get("current_neighbor")

        queue_label = "Fila" if algo_name == "BFS" else "Pilha"
        queue_str = ", ".join(str(n) for n in queue) if queue else "vazia"
        visited_str = " → ".join(str(n) for n in visited) if visited else "—"
        discovered_str = ", ".join(str(n) for n in discovered) if discovered else "—"

        items = []

        items.append(html.Div([
            html.Span("Atual: ",
                      style={"fontWeight": "600", "color": "#616161",
                             "fontSize": "11px"}),
            html.Span(str(current),
                      style={"fontWeight": "700", "fontSize": "13px",
                             "color": "#1a0e00",
                             "background": "#FEF9C3",
                             "padding": "1px 10px",
                             "borderRadius": "12px",
                             "border": "1.5px solid #b8860b"}),
        ], style={"marginBottom": "6px"}))

        if neighbor:
            items.append(
                html.Div(
                    f"{current} → {neighbor}",
                    style={"fontFamily": "Space Mono, monospace",
                           "fontSize": "12px", "fontWeight": "700",
                           "color": "#1a0e00",
                           "background": "#FEF9C3",
                           "padding": "3px 12px",
                           "borderRadius": "6px",
                           "border": "1px solid #b8860b",
                           "marginBottom": "6px",
                           "display": "inline-block"}
                )
            )

        items.append(html.Div([
            html.Div([
                html.Span(f"{queue_label}: ",
                          style={"fontWeight": "600", "color": "#616161",
                                 "fontSize": "11px"}),
                html.Span(queue_str,
                          style={"fontFamily": "Space Mono, monospace",
                                 "fontSize": "11px"}),
            ], style={"marginBottom": "3px"}),
            html.Div([
                html.Span("Visitados: ",
                          style={"fontWeight": "600", "color": "#616161",
                                 "fontSize": "11px"}),
                html.Span(visited_str,
                          style={"fontFamily": "Space Mono, monospace",
                                 "fontSize": "11px"}),
            ], style={"marginBottom": "3px"}),
            html.Div([
                html.Span("Descobertos: ",
                          style={"fontWeight": "600", "color": "#616161",
                                 "fontSize": "11px"}),
                html.Span(discovered_str,
                          style={"fontFamily": "Space Mono, monospace",
                                 "fontSize": "11px", "color": "#616161"}),
            ], style={"marginBottom": "3px"}),
        ]))

        if algo_name == "DFS" and finished:
            items.append(html.Div([
                html.Span("Finalizados: ",
                          style={"fontWeight": "600", "color": "#616161",
                                 "fontSize": "11px"}),
                html.Span(", ".join(str(n) for n in finished),
                          style={"fontFamily": "Space Mono, monospace",
                                 "fontSize": "11px", "fontWeight": "700",
                                 "color": "#212121"}),
            ], style={"marginBottom": "3px"}))

        return items




def _export_graph():
    info = graph_service.get_info()
    lines = ["NODES"]
    for node_id, pos in graph_service.positions.items():
        x = round(pos.get("x", 200), 1)
        y = round(pos.get("y", 200), 1)
        lines.append(f"{node_id} {x} {y}")

    lines.append("")
    lines.append("EDGES")
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
            _, content_string = content.split(',', 1)
            decoded = base64.b64decode(content_string).decode('utf-8')
        else:
            decoded = content

        lines = [l.strip() for l in decoded.split("\n") if l.strip()]
        if not lines:
            return False

        graph_service.clear_graph()
        graph_service.set_type(directed == "directed", weighted == "weighted")

        if lines[0].upper() == "NODES":
            section = None
            for line in lines:
                upper = line.upper()
                if upper == "NODES":
                    section = "nodes"
                    continue
                elif upper == "EDGES":
                    section = "edges"
                    continue

                parts = line.split()
                if section == "nodes" and len(parts) >= 3:
                    node_id = parts[0]
                    try:
                        x, y = float(parts[1]), float(parts[2])
                    except ValueError:
                        x, y = 200.0, 200.0
                    graph_service.add_node_at_exact(x, y, node_id)
                elif section == "edges" and len(parts) >= 2:
                    u, v = parts[0], parts[1]
                    w = int(parts[2]) if len(parts) >= 3 else 1
                    graph_service.add_edge(u, v, w)

        else:
            import random
            first = lines[0].split()
            if len(first) != 2:
                return False
            n_nodes = int(first[0])

            for i in range(n_nodes):
                node_id = chr(65 + i) if i < 26 else f"N{i}"
                x = random.randint(100, 800)
                y = random.randint(100, 500)
                graph_service.add_node(x, y, node_id)

            for line in lines[1:]:
                parts = line.split()
                if len(parts) >= 2:
                    u, v = parts[0], parts[1]
                    w = int(parts[2]) if len(parts) >= 3 else 1
                    if u in graph_service.positions and v in graph_service.positions:
                        graph_service.add_edge(u, v, w)

        return True
    except Exception as e:
        print(f"Error importing graph: {e}")
        return False




def register_callbacks(app):

    
    @app.callback(
        Output("algo-info-modal", "className"),
        Input("btn-algo-info", "n_clicks"),
        Input("modal-close", "n_clicks"),
        State("algo-info-modal", "className"),
        prevent_initial_call=True,
    )
    def toggle_modal(open_clicks, close_clicks, current_class):
        ctx = callback_context
        trigger = ctx.triggered[0]["prop_id"] if ctx.triggered else ""
        if "btn-algo-info" in trigger:
            return "modal-overlay"
        return "modal-overlay hidden"

    
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
        Output("legend-maxflow-section", "style"),
        Output("algo-interval", "disabled"),
        Output("download-file", "data"),
        Output("run-bfs", "className"),
        Output("run-dfs", "className"),
        Output("run-maxflow", "className"),
        Output("graph-direction", "className"),
        Output("graph-weight", "className"),
        Output("next-step", "disabled"),
        Output("run-all", "disabled"),
        Output("step-indicator", "children"),
        Output("step-indicator", "style"),
        Output("bottom-status-panel", "className"),

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
        Input("run-maxflow", "n_clicks"),
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
        State("maxflow-source", "value"),
        State("maxflow-sink", "value"),
        State("upload", "filename"),

        prevent_initial_call=True
    )
    def update_graph(
        add_node, hidden_add_node, hidden_add_node_at_pos,
        add_edge, hidden_delete, btn_clear,
        direction, weight,
        tap_node, tap_edge,
        run_bfs, run_dfs, run_maxflow,
        next_step, run_all, update_edge_weight,
        algo_interval,
        download_btn, upload_content,
        edge_source, edge_target,
        edit_weight,
        elements_state, zoom, pan, click_pos,
        algo_start, mf_source, mf_sink,
        upload_filename
    ):
        ctx = callback_context
        trigger = ctx.triggered[0]["prop_id"] if ctx.triggered else ""

        download_data = None
        bfs_class = "btn-algo"
        dfs_class = "btn-algo"
        mf_class = "btn-algo btn-maxflow"
        direction_class = "radio-group"
        weight_class = "radio-group"
        next_step_disabled = False
        run_all_disabled = False
        legend_mf_style = {"display": "none"}

        step_indicator_text = "0/0"
        step_indicator_style = {"display": "none"}
        bottom_panel_class = "bottom-status-panel hidden"

        zoom = zoom if isinstance(zoom, (int, float)) else 1
        pan = pan if isinstance(pan, dict) else {"x": 0, "y": 0}

        graph_service.update_positions_from_elements(elements_state)

        if click_pos:
            try:
                x, y = map(float, click_pos.split(","))
                state["last_position"] = {"x": x, "y": y}
            except Exception:
                pass

        force_clear_classes = False
        is_completion_step = False
        algo_finished = False
        completed_algo_name = None
        completed_sequence = None

        
        if "download-btn" in trigger:
            content = _export_graph()
            download_data = dict(content=content, filename="graph.txt")

        
        elif "upload" in trigger and upload_content:
            if _import_graph(upload_content, direction, weight):
                _reset_algo_state()
                force_clear_classes = True

        
        elif "add-node" in trigger or "hidden-add-node" in trigger:
            pos = state["last_position"]
            graph_service.add_node(pos["x"], pos["y"])
            _reset_algo_state()
            force_clear_classes = True

        
        elif "btn-clear" in trigger:
            graph_service.clear_graph()
            state["selected_node"] = None
            state["selected_edge"] = None
            _reset_algo_state()
            force_clear_classes = True

        
        elif "add-edge" in trigger:
            if edge_source and edge_target:
                graph_service.add_edge(
                    edge_source.strip().upper(),
                    edge_target.strip().upper(), 1)
                force_clear_classes = True

        
        elif "graph.tapNodeData" in trigger and tap_node:
            node_id = tap_node["id"]
            if state["selected_node"] is None:
                state["selected_edge"] = None
                state["selected_node"] = node_id
            else:
                if state["selected_node"] != node_id:
                    graph_service.add_edge(state["selected_node"], node_id, 1)
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
                _reset_algo_state()
                force_clear_classes = True
            elif state["selected_edge"]:
                edge_id = state["selected_edge"]
                parts = edge_id.split("-")
                if len(parts) >= 3:
                    u = parts[1]
                    v = "-".join(parts[2:]) if len(parts) > 3 else parts[2]
                    graph_service.edges_data = [
                        (a, b, w) for (a, b, w) in graph_service.edges_data
                        if not ((a == u and b == v) or
                                (not graph_service.directed and a == v and b == u))
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
                        (a, b, int(edit_weight))
                        if ((a == u and b == v) or
                            (not graph_service.directed and a == v and b == u))
                        else (a, b, w)
                        for (a, b, w) in graph_service.edges_data
                    ]
                    graph_service._rebuild_graph()
                    force_clear_classes = True

        
        elif "run-bfs" in trigger:
            start = (algo_start or "").strip().upper()
            if start and start in graph_service.graph.nodes:
                state["algo_steps"] = bfs_steps(graph_service.graph, start)
                state["algo_index"] = 0
                state["running_algo"] = "BFS"
                state["auto_running"] = False
                state["visited_sequence"] = None
                state["maxflow_source"] = None
                state["maxflow_sink"] = None
                bfs_class = "btn-algo btn-algo-active"

        
        elif "run-dfs" in trigger:
            start = (algo_start or "").strip().upper()
            if start and start in graph_service.graph.nodes:
                state["algo_steps"] = dfs_steps(graph_service.graph, start)
                state["algo_index"] = 0
                state["running_algo"] = "DFS"
                state["auto_running"] = False
                state["visited_sequence"] = None
                state["maxflow_source"] = None
                state["maxflow_sink"] = None
                dfs_class = "btn-algo btn-algo-active"

        
        elif "run-maxflow" in trigger:
            src = (mf_source or "").strip().upper()
            snk = (mf_sink or "").strip().upper()

            
            graph_service.set_type(True, True)
            direction = "directed"
            weight = "weighted"

            if src in graph_service.graph.nodes and snk in graph_service.graph.nodes:
                state["algo_steps"] = max_flow_steps(graph_service.graph, src, snk)
                state["algo_index"] = 0
                state["running_algo"] = "Fluxo Máximo"
                state["auto_running"] = False
                state["visited_sequence"] = None
                state["maxflow_source"] = src
                state["maxflow_sink"] = snk
                state["_mf_validation_error"] = False
                mf_class = "btn-algo btn-maxflow btn-algo-active"
            elif not src or not snk:
                state["algo_steps"] = []
                state["algo_index"] = 0
                state["running_algo"] = None
                state["auto_running"] = False
                state["_mf_validation_error"] = True
                state["_mf_error_msg"] = "Informe a Fonte e o Sorvedouro."
            else:
                state["algo_steps"] = []
                state["algo_index"] = 0
                state["running_algo"] = None
                state["auto_running"] = False
                state["_mf_validation_error"] = True
                state["_mf_error_msg"] = (
                    f"Vértices '{src}' ou '{snk}' não encontrados no grafo."
                )

        
        elif "next-step" in trigger:
            if state["algo_steps"] and state["algo_index"] < len(state["algo_steps"]):
                total = len(state["algo_steps"])
                if state["algo_index"] < total - 1:
                    state["algo_index"] += 1
                elif state["algo_index"] == total - 1:
                    is_completion_step = True

        
        elif "run-all" in trigger:
            if state["algo_steps"]:
                state["auto_running"] = True

        
        elif "algo-interval" in trigger and state["auto_running"] and state["algo_steps"]:
            total = len(state["algo_steps"])
            if state["algo_index"] < total - 1:
                state["algo_index"] += 1
            elif state["algo_index"] == total - 1:
                is_completion_step = True
                state["auto_running"] = False

        
        elif "graph-direction" in trigger or "graph-weight" in trigger:
            _reset_algo_state()
            force_clear_classes = True

        
        graph_service.set_type(direction == "directed", weight == "weighted")

        
        elements = _get_elements_with_flow()

        for el in elements:
            el_id = el.get("data", {}).get("id", "")
            is_edge = "source" in el.get("data", {})
            if not is_edge and el_id == state["selected_node"]:
                el["classes"] = "selected-node"
            elif is_edge and el_id == state["selected_edge"]:
                el["classes"] = "selected-edge"

        
        total_steps = len(state["algo_steps"])
        current_step = None

        if force_clear_classes:
            elements = _clear_algo_classes(elements)
        elif state["algo_steps"] and total_steps > 0:
            idx = state["algo_index"]
            if idx < total_steps:
                current_step = state["algo_steps"][idx]
                running = state.get("running_algo", "")

                if running == "Fluxo Máximo":
                    mf_src = state.get("maxflow_source")
                    mf_snk = state.get("maxflow_sink")
                    elements = _apply_maxflow_classes(elements, current_step,
                                                      mf_src, mf_snk)
                    mf_class = "btn-algo btn-maxflow btn-algo-active"
                    legend_mf_style = {"display": "block"}
                else:
                    elements = _apply_bfs_dfs_classes(elements, current_step)
                    if running == "BFS":
                        bfs_class = "btn-algo btn-algo-active"
                    elif running == "DFS":
                        dfs_class = "btn-algo btn-algo-active"

                if idx == total_steps - 1 and is_completion_step:
                    algo_finished = True
                    completed_algo_name = state.get("running_algo", "Algoritmo")
                    completed_sequence = _get_visited_sequence(state["algo_steps"])
                    state["visited_sequence"] = completed_sequence
                    state["_pending_completion"] = True

            elif idx >= total_steps:
                algo_finished = True
                completed_algo_name = state.get("running_algo", "Algoritmo")
                completed_sequence = state.get("visited_sequence", [])
                elements = _clear_algo_classes(elements)

        
        if algo_finished and state.get("_pending_completion"):
            mf_final = None
            if state.get("running_algo") == "Fluxo Máximo" and state["algo_steps"]:
                last = state["algo_steps"][-1]
                mf_final = last.get("max_flow", 0)

            state["algo_steps"] = []
            state["algo_index"] = 0
            state["running_algo"] = None
            state["auto_running"] = False
            state["_pending_completion"] = False
            bfs_class = "btn-algo"
            dfs_class = "btn-algo"
            mf_class = "btn-algo btn-maxflow"
            next_step_disabled = True
            run_all_disabled = True
            elements = _clear_algo_classes(elements)

            algo_status = _build_completion_status(
                completed_algo_name, completed_sequence, mf_final
            )
            legend_mf_style = {"display": "none"}
            bottom_panel_class = "bottom-status-panel"

        elif state.get("_mf_validation_error"):
            state["_mf_validation_error"] = False
            err_msg = state.get("_mf_error_msg", "Verifique os parâmetros.")
            algo_status = [
                html.Div([
                    html.Strong("⚠ Fluxo Máximo — ação necessária",
                                style={"color": "#dc2626", "display": "block",
                                       "marginBottom": "6px"}),
                    html.Div(err_msg,
                             style={"fontSize": "12px", "color": "#444",
                                    "marginBottom": "4px"}),
                    html.Div(
                        "O grafo foi configurado como Orientado + Com Peso "
                        "automaticamente.",
                        style={"fontSize": "11px", "color": "#16a34a",
                               "fontStyle": "italic"}
                    ),
                ])
            ]
            bottom_panel_class = "bottom-status-panel"
        else:
            algo_status = _build_algo_status(
                current_step, total_steps,
                state.get("running_algo"), state["algo_index"]
            )

        
        if state["algo_steps"] and total_steps > 0:
            idx = state["algo_index"]
            step_indicator_text = f"{idx + 1}/{total_steps}"
            step_indicator_style = {"display": "block"}
            bottom_panel_class = "bottom-status-panel"

        
        if not state["algo_steps"]:
            next_step_disabled = True
            run_all_disabled = True
        elif state["algo_index"] >= total_steps - 1:
            run_all_disabled = True
        else:
            next_step_disabled = False
            run_all_disabled = False

        
        legend_class = "algo-legend"
        if state.get("running_algo") == "Fluxo Máximo":
            legend_mf_style = {"display": "block"}

        interval_disabled = not state["auto_running"]

        
        stylesheet = _build_stylesheet(direction)

        
        info = graph_service.get_info()
        step_num = (state["algo_index"] + 1
                    if state["algo_steps"] and state["algo_index"] < total_steps
                    else None)
        show_algo = (state.get("running_algo")
                     if state["algo_steps"] and not algo_finished
                     else None)
        info_children = _build_info_box(
            info, algo_name=show_algo,
            step=step_num,
            total=total_steps if total_steps else None
        )

        return (
            elements, stylesheet, zoom, pan,
            direction, weight,
            info_children, algo_status,
            legend_class, legend_mf_style,
            interval_disabled, download_data,
            bfs_class, dfs_class, mf_class,
            direction_class, weight_class,
            next_step_disabled, run_all_disabled,
            step_indicator_text, step_indicator_style,
            bottom_panel_class,
        )



def _reset_algo_state():
    state["algo_steps"] = []
    state["algo_index"] = 0
    state["auto_running"] = False
    state["running_algo"] = None
    state["visited_sequence"] = None
    state["maxflow_source"] = None
    state["maxflow_sink"] = None


def _get_elements_with_flow():
    elements = graph_service.get_elements()
    running = state.get("running_algo")

    if running != "Fluxo Máximo":
        return elements

    steps = state.get("algo_steps", [])
    idx = state.get("algo_index", 0)

    if not steps:
        for el in elements:
            if "source" in el.get("data", {}):
                cap = el["data"].get("weight", 1)
                el["data"]["label"] = f"0/{cap}"
                el["data"]["flow"] = 0
                el["data"]["capacity"] = cap
        return elements

    if idx >= len(steps):
        idx = len(steps) - 1

    current_step = steps[idx]
    flow_on_edges = current_step.get("flow_on_edges", {})
    capacity = current_step.get("capacity", {})

    for el in elements:
        if "source" in el.get("data", {}):
            src = el["data"]["source"]
            tgt = el["data"]["target"]
            cap = capacity.get((src, tgt), el["data"].get("weight", 1))

            if cap <= 0:
                continue

            f = flow_on_edges.get((src, tgt), 0)
            f = max(0, f)

            el["data"]["label"] = f"{f}/{cap}"
            el["data"]["flow"] = f
            el["data"]["capacity"] = cap

            el["data"]["saturated"] = 1 if f >= cap else 0

    return elements


def _build_completion_status(algo_name, sequence, mf_final=None):
    if algo_name == "Fluxo Máximo":
        return [
            html.Div([
                html.Strong("✓ Fluxo Máximo concluído",
                            style={"color": "#8B004B", "display": "block",
                                   "marginBottom": "10px",
                                   "fontSize": "13px",
                                   "borderBottom": "1.5px solid #ffb6d9",
                                   "paddingBottom": "6px"}),
                html.Div([
                    html.Span("Fluxo máximo = ",
                              style={"color": "#616161", "fontSize": "12px",
                                     "fontWeight": "600"}),
                    html.Span(str(mf_final),
                              style={"fontSize": "26px", "fontWeight": "900",
                                     "color": "#16a34a",
                                     "fontFamily": "Space Mono, monospace"}),
                ], style={"textAlign": "center",
                          "background": "#f0fdf4",
                          "padding": "10px 16px",
                          "borderRadius": "10px",
                          "border": "2px solid #16a34a",
                          "marginBottom": "8px"}),
                html.Div(
                    "Nenhum caminho aumentante restante. Algoritmo finalizado.",
                    style={"color": "#9E9E9E", "fontSize": "11px",
                           "fontStyle": "italic"}
                ),
            ])
        ]
    else:
        seq_display = _format_sequence_display(sequence, algo_name)
        return [
            html.Div([
                html.Strong(f"✓ {algo_name} concluído",
                            style={"color": "#8B004B", "display": "block",
                                   "marginBottom": "8px",
                                   "fontSize": "13px",
                                   "borderBottom": "1.5px solid #ffb6d9",
                                   "paddingBottom": "6px"}),
                html.Div("Sequência visitada:",
                         style={"fontWeight": "600", "color": "#616161",
                                "fontSize": "11px", "marginBottom": "6px"}),
                html.Div(seq_display,
                         style={"display": "flex", "flexWrap": "wrap",
                                "alignItems": "center",
                                "justifyContent": "flex-start",
                                "gap": "2px", "marginBottom": "6px",
                                "padding": "8px",
                                "background": "#fff0f6",
                                "borderRadius": "8px",
                                "border": "1.5px solid #ffb6d9"}),
                html.Div(f"Total: {len(sequence)} vértice(s)",
                         style={"color": "#9E9E9E", "fontSize": "11px"}),
            ])
        ]