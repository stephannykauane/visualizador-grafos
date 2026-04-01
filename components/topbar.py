from dash import html, dcc

def create_topbar():
    return html.Div([
        html.Div([
            html.Span("<3", style={"fontSize": "20px"}),
            "Visualizador de grafos rosa"
        ], className="topbar-logo"),

        html.Div([
            dcc.Upload(
                html.Button("Upload", className="button",
                            style={"width": "auto", "padding": "7px 16px", "marginBottom": 0}),
                id="upload"
            ),
            html.Button("Download", id="download-btn", className="button",
                        style={"width": "auto", "padding": "7px 16px", "marginBottom": 0}),
            dcc.Download(id="download-file"),
        ], className="topbar-actions")
    ], className="topbar")