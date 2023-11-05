import json
from dash import Dash, dcc, html, Input, Output, clientside_callback, callback, ClientsideFunction, State
from dash.exceptions import PreventUpdate
import os
import pathlib

from get_model import build_dragonfly_model, add_apertures, df_to_hb, add_sensor_grids
from submit_study import run_study

app = Dash(__name__, external_scripts=[{"src": "./static/forma.mjs", "type": "module"}])

# external_scripts = [{"src": "./assets/forma.js", "type": "module"}]

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
    
    if not data:
        return []
    ## create model
    data = json.loads(data)
    print('Creating the Dragonfly model')
    model = build_dragonfly_model(data)
    print('Adding apertures')
    model = add_apertures(model, win_height=2, win_width=1)
    print('Translate model to a Honeybee model')
    model = df_to_hb(model)
    print('Add sensor grids to model')
    model = add_sensor_grids(model)
    print('Saving model as HBJSON')
    p = model.to_hbjson('model.hbjson', folder='.')
    ## submit study
    print('Submitting simulation to Pollination')
    run_study(False)
    print('Loading results')
    ## return the reuslts
    res_folder = pathlib.Path('results', 'results')
    results = []
    for grid in model.properties.radiance.sensor_grids:
        res_file = res_folder.joinpath(f'{grid.display_name}.res')
        res = res_file.read_text().splitlines()
        for pt, res in zip(grid.positions, res):
            results.append({'x': pt[0], 'y': pt[1], 'z': pt[2], 'v': float(res)})
    print('Done and done!')
    return results


if __name__ == "__main__":
    app.run(debug=True, port=8082)
