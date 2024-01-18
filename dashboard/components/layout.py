from ..etls import DistritoTransformer, SetoresTransformer
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_daq as daq
from dash import Dash, html, Output, Input
from dash_extensions.javascript import arrow_function

class Layout:

    def __init__(self):
        
        Distritos = DistritoTransformer()

        Setores = SetoresTransformer()

        self.distritos = Distritos()
        self.setores = Setores()

    def criar_camadas_do_mapa(self, distrito_toggle: bool):
        camadas = [dl.LayersControl(
                [dl.BaseLayer(
                    dl.TileLayer(),
                    name='Base',
                    checked=True
                )] + [
                    dl.Overlay(dl.Pane(dl.GeoJSON(data=self.distritos, id="distritos", format='geobuf',
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
                    dl.Overlay(children=[dl.Pane(dl.GeoJSON(data=self.setores, id="setores", format='geobuf',
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
        
    def criar_o_mapa(self, camadas):
        html.Div([
            dl.Map(center=[-23.5475, -46.6375],
                children=camadas, id="map"),
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
    
    def pipeline(self,):
        camadas = self.criar_camadas_do_mapa(False)
        layout = self.criar_o_mapa(camadas)

        return layout
    
    def __call__(self,):
        
        return self.pipeline()