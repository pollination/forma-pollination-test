from dash import Dash, dcc, html, Input, Output, clientside_callback, ClientsideFunction

app = Dash(__name__, external_scripts=[{"src": "./static/forma.mjs", "type": "module"}])

# external_scripts = [{"src": "./assets/forma.js", "type": "module"}]

app.layout = html.Div(
    [
        html.Div(
            ["Input: ", dcc.Input(id="my-input", value="initial value", type="text")]
        ),
        html.Button("Submit", id="button", n_clicks=0),
        html.Br(),
        html.Div(id="my-output"),
    ]
)

clientside_callback(
    ClientsideFunction(namespace="forma", function_name="getVolumes"),
    Output("my-output", "children"),
    [Input("button", "n_clicks")],
)


if __name__ == "__main__":
    app.run(debug=True, port=8081)
