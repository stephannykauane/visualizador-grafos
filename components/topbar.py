from dash import html, dcc


def create_topbar():
    return html.Div([
        html.Div([
            html.Span("♡", className="topbar-logo-heart"),
            "Visualizador de Grafos Rosa"
        ], className="topbar-logo"),

        html.Div([
            dcc.Upload(
                html.Button("↑ Upload", className="btn-topbar"),
                id="upload"
            ),
            html.Button("↓ Download", id="download-btn", className="btn-topbar"),
            dcc.Download(id="download-file"),
        ], className="topbar-actions")
    ], className="topbar")