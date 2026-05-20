from dash import html, dcc
import dash_cytoscape as cyto


def create_workspace():
    return html.Div([

        html.Button(id="hidden-add-node", style={"display": "none"}, n_clicks=0),
        html.Button(id="hidden-delete", style={"display": "none"}, n_clicks=0),
        html.Button(id="hidden-add-node-at-pos", style={"display": "none"}, n_clicks=0),
        dcc.Input(id="hidden-click-position-string", type="text",
                  style={"display": "none"}, value=""),

        html.Div([
            html.Div([
                html.Button("✕", id="modal-close", className="modal-close"),
                html.Div("Fluxo Máximo", className="modal-title"),
                html.Div("Ford-Fulkerson com BFS · Edmonds-Karp",
                         className="modal-subtitle"),

                html.Div("Objetivo", className="modal-section-title"),
                html.P(
                    "Encontrar o maior fluxo possível entre uma fonte (S) e um "
                    "sorvedouro (T) em um grafo orientado ponderado.",
                    style={"fontSize": "13px", "color": "#444",
                           "lineHeight": "1.6", "marginBottom": "4px"}
                ),

                html.Div("Como funciona", className="modal-section-title"),
                html.Div([
                    html.Div([
                        html.Div("1", className="modal-step-num"),
                        html.Span("Executa BFS no grafo residual para encontrar um "
                                  "caminho da fonte ao sorvedouro (caminho aumentante).")
                    ], className="modal-step"),
                    html.Div([
                        html.Div("2", className="modal-step-num"),
                        html.Span("Identifica o gargalo: a menor capacidade residual "
                                  "ao longo do caminho.")
                    ], className="modal-step"),
                    html.Div([
                        html.Div("3", className="modal-step-num"),
                        html.Span("Atualiza as capacidades residuais: subtrai o "
                                  "gargalo nas arestas diretas e soma nas reversas.")
                    ], className="modal-step"),
                    html.Div([
                        html.Div("4", className="modal-step-num"),
                        html.Span("Repete até não existir mais nenhum caminho "
                                  "aumentante. O fluxo acumulado é o fluxo máximo.")
                    ], className="modal-step"),
                ]),

                html.Div("Interpretação dos pesos", className="modal-section-title"),
                html.Div([
                    "Os pesos das arestas representam ",
                    html.Strong("capacidades"),
                    " (fluxo máximo permitido).",
                    html.Br(),
                    "Durante a execução, os rótulos mostram ",
                    html.Code("fluxo / capacidade",
                              style={"background": "#f5f5f5",
                                     "padding": "1px 6px",
                                     "borderRadius": "4px",
                                     "fontSize": "12px"}),
                    ".",
                ], style={"fontSize": "13px", "color": "#444",
                          "lineHeight": "1.7"}),

                html.Div(className="modal-example", children=[
                    "A ──10──▶ B    significa: capacidade máxima = 10",
                    html.Br(),
                    "Durante execução: A ──3/10──▶ B  (3 unidades fluindo de 10 possíveis)",
                ]),

                html.Div("Cores na visualização", className="modal-section-title"),
                html.Div([
                    html.Span("🟡 Dourado", className="modal-tag modal-tag-pink"),
                    "  Caminho aumentante ativo",
                    html.Br(),
                    html.Span("🔵 Azul tracejado", className="modal-tag modal-tag-pink"),
                    "  Aresta residual",
                    html.Br(),
                    html.Span("🟢 Verde", className="modal-tag modal-tag-pink"),
                    "  Fonte (S)",
                    html.Br(),
                    html.Span("🔴 Vermelho", className="modal-tag modal-tag-pink"),
                    "  Sorvedouro (T)",
                    html.Br(),
                    html.Span("⬜ Desbotado", className="modal-tag modal-tag-pink"),
                    "  Fora do caminho atual",
                ], style={"fontSize": "13px", "color": "#444",
                          "lineHeight": "2.1"}),

                html.Div("Requisitos", className="modal-section-title"),
                html.Div([
                    "Este algoritmo requer: ",
                    html.Strong("grafo orientado"),
                    " + ",
                    html.Strong("arestas com peso (capacidade)"),
                    ". Ao clicar em 'Fluxo Máximo', o sistema configura isso ",
                    html.Strong("automaticamente"),
                    ".",
                ], style={"fontSize": "13px", "color": "#444",
                          "lineHeight": "1.7",
                          "background": "#fff0f6",
                          "padding": "10px 14px",
                          "borderRadius": "8px",
                          "border": "1.5px solid #ffb6d9",
                          "marginTop": "4px"}),

            ], className="modal-card"),
        ], id="algo-info-modal", className="modal-overlay hidden"),


        html.Div([
            html.Div([
                html.Span("Algoritmos"),
                html.Div(id="step-indicator", className="step-badge",
                         style={"display": "none"},
                         children="0/0"),
            ], className="floating-algo-panel-title"),

            # BFS / DFS
            html.Div("BFS / DFS", className="section-label",
                     style={"marginTop": "0"}),
            dcc.Input(id="algo-start", type="text",
                      placeholder="Vértice inicial (ex: A)",
                      className="input-field algo-input"),
            html.Div([
                html.Button("BFS", id="run-bfs", className="btn-algo"),
                html.Button("DFS", id="run-dfs", className="btn-algo"),
            ], className="algo-btn-row"),

            html.Hr(style={"margin": "8px 0"}),

            # Fluxo Máximo
            html.Div([
                html.Span("Fluxo Máximo"),
                html.Span("auto-config", className="auto-config-badge"),
            ], className="maxflow-label"),

            dcc.Input(id="maxflow-source", type="text",
                      placeholder="Fonte (ex: S)",
                      className="input-field algo-input"),
            dcc.Input(id="maxflow-sink", type="text",
                      placeholder="Sorvedouro (ex: T)",
                      className="input-field algo-input"),

            html.Div([
                html.Button("Fluxo Máximo", id="run-maxflow",
                            className="btn-algo btn-maxflow",
                            style={"flex": "1", "marginBottom": "0"}),
                html.Button("ⓘ", id="btn-algo-info", className="btn-info",
                            n_clicks=0),
            ], style={"display": "flex", "alignItems": "center",
                      "gap": "6px", "marginBottom": "4px"}),

            html.Hr(style={"margin": "8px 0"}),

            # Controles de execução
            html.Div([
                html.Button("▶ Próximo", id="next-step", className="btn-next"),
                html.Button("⚡ Executar Tudo", id="run-all", className="btn-next",
                            style={"background": "linear-gradient(90deg,#ff1493,#8B004B)"}),
            ], className="algo-ctrl-row"),

        ], className="floating-algo-panel"),


        html.Div([

            # Info do Grafo
            html.Div([
                html.H3("Grafo", className="info-panel-title"),
                html.Div(id="graph-info", className="info-box", children=[
                    html.Div([html.Div(className="info-dot"),
                              html.Span([html.Strong("Vértices: "), "0"])],
                             className="info-row"),
                    html.Div([html.Div(className="info-dot"),
                              html.Span([html.Strong("Arestas: "), "0"])],
                             className="info-row"),
                    html.Div([html.Div(className="info-dot"),
                              html.Span([html.Strong("Tipo: "), "Não Orientado"])],
                             className="info-row"),
                    html.Div([html.Div(className="info-dot"),
                              html.Span([html.Strong("Peso: "), "Sem Peso"])],
                             className="info-row"),
                ]),
            ], className="info-panel"),

            # Legenda — SEMPRE VISÍVEL, nunca empurrada
            html.Div([
                html.Div("Legenda", className="legend-title"),

                # Estados universais BFS/DFS
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#FFFFFF",
                                    "border": "2px solid #212121"}),
                    "Não visitado"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#9E9E9E",
                                    "border": "2px solid #616161"}),
                    "Descoberto"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#212121",
                                    "border": "2px solid #000"}),
                    "Processado"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#FFD700",
                                    "border": "2px solid #b8860b"}),
                    "Atual"
                ], className="legend-item"),

                # Seção Fluxo Máximo — toggle via callback
                html.Div(id="legend-maxflow-section", children=[
                    html.Hr(style={"margin": "6px 0", "opacity": "0.4"}),
                    html.Div("Fluxo Máximo",
                             style={"fontSize": "10px", "color": "#8B004B",
                                    "fontWeight": "700",
                                    "textTransform": "uppercase",
                                    "letterSpacing": "0.8px",
                                    "marginBottom": "5px"}),
                    html.Div([
                        html.Div(className="legend-dot",
                                 style={"background": "#FFD700",
                                        "border": "2px solid #b8860b"}),
                        "Caminho aumentante"
                    ], className="legend-item"),
                    html.Div([
                        html.Div(className="legend-dot",
                                 style={"background": "#3b82f6",
                                        "border": "2px solid #1d4ed8"}),
                        "Aresta residual"
                    ], className="legend-item"),
                    html.Div([
                        html.Div(className="legend-dot",
                                 style={"background": "#16a34a",
                                        "border": "2px solid #14532d"}),
                        "Fonte (S)"
                    ], className="legend-item"),
                    html.Div([
                        html.Div(className="legend-dot",
                                 style={"background": "#dc2626",
                                        "border": "2px solid #7f1d1d"}),
                        "Sorvedouro (T)"
                    ], className="legend-item"),
                    html.Div([
                        html.Div(className="legend-dot",
                                 style={"background": "#e5e7eb",
                                        "border": "2px solid #9ca3af",
                                        "opacity": "0.5"}),
                        "Fora do caminho"
                    ], className="legend-item"),
                ], style={"display": "none"}),

            ], id="algo-legend", className="algo-legend"),

        ], className="right-sidebar"),


        html.Div([
            html.Div([
                html.Span("Status do Algoritmo", className="bottom-status-title"),
            ], className="bottom-status-header"),
            html.Div(
                id="algo-status",
                className="bottom-status-body",
                children="Nenhum algoritmo rodando.",
            ),
        ], id="bottom-status-panel", className="bottom-status-panel hidden"),

        # ══════════════════════════════════════════════════════════
        # CYTOSCAPE — Grafo Principal
        # ══════════════════════════════════════════════════════════
        cyto.Cytoscape(
            id="graph",
            elements=[],
            style={"width": "100%", "height": "100%"},
            layout={"name": "preset"},
            zoom=1,
            pan={"x": 0, "y": 0},
            minZoom=0.2,
            maxZoom=5,
            responsive=False,
            autoRefreshLayout=False,
            stylesheet=_base_stylesheet(),
        ),

        html.Div(
            "Clique em dois vértices para conectar  •  V = novo vértice  •  Backspace = apagar",
            className="workspace-hint"
        ),

    ], className="workspace")


def _base_stylesheet():
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
                "target-arrow-shape": "none",
                "curve-style": "bezier",
                "width": 2.5,
                "label": "data(label)",
                "font-size": "11px",
                "font-weight": "600",
                "color": "#212121",
                "text-background-color": "#FFFFFF",
                "text-background-opacity": 1,
                "text-background-padding": "2px",
                "text-background-shape": "roundrectangle",
                "text-border-opacity": 1,
                "text-border-width": 1,
                "text-border-color": "#BDBDBD",
                "text-rotation": "autorotate",
                "transition-property": "line-color, width, opacity",
                "transition-duration": "0.25s",
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
             "width": 4,
         }},

        # Max Flow
        {"selector": ".maxflow-path",
         "style": {
             "line-color": "#FFD700", "target-arrow-color": "#FFD700",
             "target-arrow-shape": "triangle", "width": 5,
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