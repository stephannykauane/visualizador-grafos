from dash import html, dcc
import dash_cytoscape as cyto

def create_workspace():
    return html.Div([
        html.Button(id="hidden-add-node", style={"display": "none"}, n_clicks=0),
        html.Button(id="hidden-delete", style={"display": "none"}, n_clicks=0),
        html.Button(id="hidden-add-node-at-pos", style={"display": "none"}, n_clicks=0),
        dcc.Input(id="hidden-click-position-string", type="text", style={"display": "none"}, value=""),

        html.Div([
            html.Div([
                html.H3("Algoritmos", className="algo-panel-title"),
                dcc.Input(id="algo-start", type="text", placeholder="Vértice inicial (ex: A)", className="input-field algo-input"),
                html.Div([
                    html.Button("BFS", id="run-bfs", className="btn-algo", style={"marginRight": "8px"}),
                    html.Button("DFS", id="run-dfs", className="btn-algo"),
                ], style={"display": "flex", "marginBottom": "8px"}),
                html.Div(id="algo-status", className="algo-status", children="Nenhum algoritmo rodando."),
                html.Button("Próximo Passo", id="next-step", className="btn-next", style={"marginTop": "4px"}),
                html.Button("Executar Tudo", id="run-all", className="btn-next",
                            style={"background": "linear-gradient(90deg,#c2185b,#8B004B)", "marginTop": "4px"}),
            ], className="algo-panel"),
            
           
            html.Div([
                html.H3("Informações do Grafo", className="info-panel-title"),
                html.Div(id="graph-info", className="info-box", children=[
                    html.Div([html.Div(className="info-dot"), "Vértices: 0"], className="info-row"),
                    html.Div([html.Div(className="info-dot"), "Arestas: 0"], className="info-row"),
                    html.Div([html.Div(className="info-dot"), "Tipo: Não Orientado"], className="info-row"),
                    html.Div([html.Div(className="info-dot"), "Peso: Sem Peso"], className="info-row"),
                ]),
            ], className="info-panel"),

          
            html.Div([
                html.Div("Legenda", className="legend-title"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#FFD700", "border": "2px solid #b8860b"}),
                    "Vértice atual"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#87CEFA", "border": "2px solid #4682b4"}),
                    "Já visitado"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#b0f0c0", "border": "2px solid #2e8b57"}),
                    "Na fila/pilha"
                ], className="legend-item"),
                html.Div([
                    html.Div(className="legend-dot",
                             style={"background": "#ff69b4", "border": "2px solid #c2185b"}),
                    "Não visitado"
                ], className="legend-item"),
            ], id="algo-legend", className="algo-legend"),

        ], className="workspace-panels"),

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
            stylesheet=[
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
                        "target-arrow-shape": "none",
                        "source-arrow-shape": "none",
                    }
                },
                {
                    "selector": "[directed = 1]",
                    "style": {
                        "target-arrow-shape": "triangle",
                    }
                },
                {
                    "selector": ".selected-node",
                    "style": {
                        "background-color": "#ff00cc",
                        "border-width": 4,
                        "border-color": "#8B004B",
                        "box-shadow": "0 0 12px #ff00cc",
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
        ),

        html.Div("Clique em dois vértices para conectar  •  V = novo vértice  •  Del = apagar selecionado",
                 className="workspace-hint"),

    ], className="workspace")