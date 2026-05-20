from dash import html, dcc


def create_sidebar():
    return html.Div([
        html.H2("Configurações", className="sidebar-title"),

        # Orientação
        html.Div("Orientação", className="section-label"),
        dcc.RadioItems(
            id="graph-direction",
            options=[
                {"label": "Não Orientado", "value": "undirected"},
                {"label": "Orientado", "value": "directed"},
            ],
            value="undirected",
            className="radio-group",
            inputStyle={"display": "none"},
            labelStyle={"cursor": "pointer"},
        ),

        # Peso
        html.Div("Peso das Arestas", className="section-label"),
        dcc.RadioItems(
            id="graph-weight",
            options=[
                {"label": "Sem Peso", "value": "unweighted"},
                {"label": "Com Peso", "value": "weighted"},
            ],
            value="unweighted",
            className="radio-group",
            inputStyle={"display": "none"},
            labelStyle={"cursor": "pointer"},
        ),

        html.Hr(),

        # Vértices
        html.Div("Vértices", className="section-label"),
        html.Button("+ Adicionar Vértice  (V)", id="add-node",
                    className="btn-primary"),

        html.Hr(),

        # Conectar
        html.Div("Conectar Vértices", className="section-label"),
        dcc.Input(id="edge-source", type="text",
                  placeholder="De (ex: A)", className="input-field"),
        dcc.Input(id="edge-target", type="text",
                  placeholder="Para (ex: B)", className="input-field"),
        html.Button("Conectar", id="add-edge", className="btn-secondary"),

        html.Hr(),

        # Editar aresta
        html.Div("Editar Aresta Selecionada", className="section-label"),
        dcc.Input(id="edit-edge-weight", type="number",
                  placeholder="Novo peso", className="input-field"),
        html.Button("Atualizar Peso", id="update-edge-weight",
                    className="btn-secondary"),

        html.Hr(),

        # Limpar
        html.Button("🗑 Limpar Grafo", id="btn-clear", className="btn-danger"),

        # Interval para execução automática
        dcc.Interval(id="algo-interval", interval=900, n_intervals=0,
                     disabled=True),

    ], className="sidebar")