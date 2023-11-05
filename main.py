import json
from dash import Dash, dcc, html, Input, Output, clientside_callback, callback, ClientsideFunction, State
from dash.exceptions import PreventUpdate
app = Dash(__name__, external_scripts=[{"src": "./static/forma.mjs", "type": "module"}])

app.layout = html.Div(
    [
        html.Button("Analyze", id="button", n_clicks=0),
        html.Br(),
        dcc.Store(id="geometry"),
        dcc.Store(id="result", storage_type='local'),
        dcc.Store(id="void")
    ]
)

clientside_callback(
    ClientsideFunction(namespace="forma", function_name="getVolumes"),
    Output("geometry", "data"),
    [Input("button", "n_clicks")],
)

clientside_callback(
    ClientsideFunction(namespace="forma", function_name="vizualize"),
    Output("void", "data"),
    Input("result", "modified_timestamp"),
    State("result", "data"),
)

@callback(Output("result", 'data'),
            Input("geometry", 'modified_timestamp'),
            State("geometry", 'data'))
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate
    with open("./results.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    app.run(debug=True, port=8082)
