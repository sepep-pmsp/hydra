from dash import Dash, Input, Output
from dash.dcc import Loading
from dash_extensions.javascript import arrow_function
from dash_leaflet import (
    Map as dlMap,
    Pane,
    GeoJSON,
    Overlay,
    LayersControl,
    BaseLayer,
    TileLayer,
)


class Map:
    
    @staticmethod
    def setores_overlay_children(setor_geobuf: str) -> Pane:
        pane = Pane(GeoJSON(data=setor_geobuf, id="setores", format='geobuf',
                            hideout=dict(
                                selected=[]),
                            options={
                                "style": {
                                    'color': 'rgba(0,0,0,0)',
                                    'fillColor': 'red',
                                    'fillOpacity': 0.8
                                }},
                            hoverStyle=arrow_function(
                                dict(weight=5, color='red', dashArray='', fillOpacity=0.5)),
                            zoomToBounds=True),
                    name='setores_pane',
                    style={'zIndex': 420}
                    )
        return pane

    @staticmethod
    def setor_detalhes_overlay_children(setor_geobuf: str) -> Pane:
        pane = Pane(GeoJSON(data=setor_geobuf, id="setor_detalhes", format='geobuf',
                            hideout=dict(
                                selected=[]),
                            options={
                                "style": {
                                    'color': 'red',
                                    'fillColor': '#ffa7a1',
                                    'fillOpacity': 1
                                }},
                            hoverStyle=arrow_function(
                                dict(weight=5, dashArray=''))),
                    name='setor_detalhes_pane',
                    style={'zIndex': 421}
                    )
        return pane

    @staticmethod
    def limite_municipal_children(limite_municipal_geobuf:str) -> GeoJSON:
        geojson = GeoJSON(data=limite_municipal_geobuf, id="limite_municipal", format='geobuf',
                          options={
                              "style": {'color': '#949494',
                                        'fillColor': '#c0c0c0',
                                        'fillOpacity': 0.5}},
                          )
        return geojson

    @staticmethod
    def distrito_municipal_children(distrito_geobuf: str) -> GeoJSON:
        geojson = GeoJSON(data=distrito_geobuf, id="distritos", format='geobuf',
                          options={
                              "style": {'color': 'rgba(0,0,0,0)',
                                        'fillColor': 'green',
                                        'fillOpacity': 0.8}},
                          hoverStyle=arrow_function(
                              dict(weight=5, color='#666', dashArray=''))
                          )
        return geojson

    @staticmethod
    def map_children():
        base = [BaseLayer(
            TileLayer(),
            name='Base',
            checked=True
        )]
        overlay = []
        zindex = 401
        overlay.append(
            Overlay(Pane(children=[],
                         id='limite_municipal_pane',
                         name='limite_municipal_pane',
                         # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                         # portanto os valores personalizados devem estar entre 400 e 500
                         style={'zIndex': zindex}
                         ),
                    id='limite_municipal_ol',
                    name='limite_municipal_ol',
                    checked=True
                    )
        )
        zindex += 1
        overlay.append(
            Overlay(Pane(children=[],
                         id='distritos_pane',
                         name='distritos_pane',
                         # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                         # portanto os valores personalizados devem estar entre 400 e 500
                         style={'zIndex': zindex}
                         ),
                    id='distritos_ol',
                    name='distritos_ol',
                    checked=False
                    )
        )
        zindex += 1

        overlay.append(
            Overlay(children=[],
                    id="setores_ol",
                    name='setores_ol',
                    checked=True
                    )
        )

        overlay.append(
            Overlay(children=[],
                    id="setor_detalhes_ol",
                    name='setor_detalhes_ol',
                    checked=True
                    )
        )

        return [
            LayersControl(
                base + overlay,
                id='layers-control'
            ),
        ]

    @staticmethod
    def get_component():
        return Loading(
            dlMap(center=[-23.5475, -46.6375],
                zoom=10,
                children=Map.map_children(),
                id="map",
                className='p-3')
        )
