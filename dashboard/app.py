import dash_leaflet as dl

import dash_daq as daq
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function



from etls.etl_scripts.distrito_municipal.transformer import Transformer as Transformer_distritos
from etls.etl_scripts.setor_censitario.transformer import Transformer as Transformer_setores

distritos = Transformer_distritos()
setores = Transformer_setores()
distritos = distritos()
setores = setores()


def map_children(distrito_toggle: bool):
    return [dl.LayersControl(
            [dl.BaseLayer(
                dl.TileLayer(),
                name='Base',
                checked=True
            )] + [
                dl.Overlay(dl.Pane(dl.GeoJSON(data=distritos, id="distritos", format='geobuf',
                                      options={
                                      "style":{'color': 'green',
                                             'fillColor': 'green',
                                             'fillOpacity': 0.5}},
                                      hoverStyle=arrow_function(
                                          dict(weight=5, color='#666', dashArray=''))
                                    ),
                           name='distritos_pane',
                           # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                           # portanto os valores personalizados devem estar entre 400 e 500
                           style={'zIndex': 410}
                           ),
                           id='distritos_ol',
                           name='distritos_ol',
                           checked=distrito_toggle
                           ),
                dl.Overlay(children=[dl.Pane(dl.GeoJSON(data=setores, id="setores", format='geobuf',
                       hideout=dict(selected=[]),
                       options={
                       "style": {
                           'color': 'red',
                           'fillColor': 'red'
                       }},
                       hoverStyle=arrow_function(
                           dict(weight=5, color='red', dashArray='', fillOpacity=0.5)),
                       zoomToBounds=True),
                        name='setores_pane',
                        style={'zIndex': 420}
                    )],
                        id="setores_ol",
                        name='setores_ol',
                        checked=True
                    ),

                ],
            id='layers-control'),]


# Create example app.
app = Dash()
app.layout = html.Div([
    dl.Map(center=[-23.5475, -46.6375],
           children=map_children(False), id="map"),
    html.Div([
        html.Div(id='setor_data'),
        html.Div([
            html.H2('Distrito', id='distrito_header', className='layer_header'),
            daq.BooleanSwitch(
                id='distrito_toggle',
                label="Exibir no mapa",
                on=False,
                className='layer_toggle',
            )
        ], id='distrito_wrapper'
        )
    ],
    id="info_panel"),
    html.Div(children=[],id='message')
],
    id="wrapper"
)

@app.callback(
    Output("setor_data", "children"),
    Input("distritos", "click_feature"),
    Input("setores", "click_feature"),
    prevent_initial_call=True
)
def feature_click(f1, f2):
    msg = None
    if f1 is not None:
        msg = f1['properties']['nm_distrito_municipal']
    if f2 is not None:
        msg = f2['properties']['cd_original_setor_censitario']

    if msg is not None:
        return f"You clicked {msg}"


@app.callback(
    Output('distritos_ol', 'checked'),
    Input('distrito_toggle', 'on')
)
def update_checked_layers(value):
    return value

if __name__ == '__main__':
    app.run_server(debug=True, port=7777)
