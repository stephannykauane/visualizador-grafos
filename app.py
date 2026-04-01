from dash import Dash, html
from components.sidebar import create_sidebar
from components.workspace import create_workspace
from components.topbar import create_topbar
from callbacks.graph_callbacks import register_callbacks

app = Dash(__name__)
app.title = "Visualizador de grafos"

app.layout = html.Div([
    create_topbar(),
    html.Div([
        create_sidebar(),
        create_workspace()
    ], style={"display": "flex", "height": "90vh"})
])

register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True)