from typing import Any
import dash_bootstrap_components as dbc
from dash import html
from dash_extensions.javascript import arrow_function

import dash_leaflet as dl
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
    SETORES_OVERLAY_ID='setores_ol'
    LIMITE_MUNICIPAL_PANE_ID='limite_municipal_pane'
    DISTRITOS_PANE_ID='distritos_pane'
    SETOR_DETALHES_OVERLAY_ID='setor_detalhes_ol'
    DISTRITOS_OVERLAY_ID='distritos_ol'
    SETORES_GEOJSON_ID='setores'
    LIMITE_MUNICIPAL_OVERLAY_ID= 'limite_municipal_ol'


    def __init__(self, 
                 url:str = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', 
                 attribution:str = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> ',
                 callback_load_children:bool = False,
                 ) -> None:
        

        
        self.callback_load_children = callback_load_children
        self.url = url
        self.attribuition = attribution
        
        
        self.style = {
            'z-index': '0',
            'height': '80vh'}
        self.classNames = 'base_map_div'
        
        self.ids = {'map': 'map',
                    'setores_overlay': Map.SETORES_OVERLAY_ID,
                    'limite_municipal_pane': Map.LIMITE_MUNICIPAL_PANE_ID,
                    'distritos_pane': Map.DISTRITOS_PANE_ID,
                    'setor_details_overlay': Map.SETOR_DETALHES_OVERLAY_ID,
                    'setores_geojson': Map.SETORES_GEOJSON_ID,
                    'distritos_overlay': Map.DISTRITOS_OVERLAY_ID,
                    'limite_municipal_ol': Map.LIMITE_MUNICIPAL_OVERLAY_ID}
        
        self.center = [-23.5475, -46.6375]
        self.zoom = 10
        
    def setores_overlay_children(setor_geobuf: str) -> Pane:
        pane = Pane(GeoJSON(data=setor_geobuf, id=Map.SETORES_GEOJSON_ID, format='geobuf',
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
    
    def limite_municipal_children(limite_municipal_geobuf:str) -> GeoJSON:
        geojson = GeoJSON(data=limite_municipal_geobuf, id="limite_municipal", format='geobuf',
                          options={
                              "style": {'color': '#949494',
                                        'fillColor': '#c0c0c0',
                                        'fillOpacity': 0.5}},
                          )
        return geojson

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


    def generate_map_children(self, url:str, attribution:str) -> html.Div:
        overlay = []
        zindex = 401


        base_layer = [dl.BaseLayer(
            dl.TileLayer(url=url, maxZoom=20, attribution=attribution),
            name='Base',
            checked=True
        )]



        overlay.append(
            dl.Overlay(dl.Pane(children=[],
                        id=self.ids.get('limite_municipal_pane'),
                        name='limite_municipal_pane',
                        # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                        # portanto os valores personalizados devem estar entre 400 e 500
                        style={'zIndex': zindex}
                        ),
                        id=self.ids.get('limite_municipal_ol'),
                        name='limite_municipal_ol',
                        checked=True
                )
        )
        zindex += 1


        overlay.append(
            dl.Overlay(dl.Pane(children=[],
                            id=self.ids.get('distritos_pane'),
                                name='distritos_pane',
                                # O z-index padrão do overlay pane é 400 e o próximo pane (shadow) é 500,
                                # portanto os valores personalizados devem estar entre 400 e 500
                                style={'zIndex': zindex}
                                ),
                        id=self.ids.get('distritos_overlay'),
                        name='distritos_ol',
                        checked=False
                        )
        )
        zindex += 1


        overlay.append(
            dl.Overlay(children=[],
                        id=self.ids.get('setores_overlay'),
                        name='setor_detalhes_ol',
                        checked=True
                        )
        )


        overlay.append(
            dl.Overlay(children=[],
                        id=self.ids.get('setor_details_overlay'),
                        name='setor_detalhes_ol',
                        checked=True
                        )
        )


        return [
            html.Div(dl.LayersControl(
                base_layer + overlay,
                id='layers-control'
            ))
            ,
        ]

        

    def generate_base_map(self,map_children) -> html.Div :
        base_map = dl.Map(center=self.center,
                zoom=self.zoom,
                children=map_children,
                id=self.ids.get('map'),
                className=self.classNames,
                style=self.style)
        
        base_map_div = html.Div(base_map)

        return base_map_div

    
    def pipeline(self) -> html.Div:

        if self.callback_load_children == False:

            base_map = self.generate_base_map(self.generate_map_children(url=self.url, attribution=self.attribuition))
            base_map_div = html.Div(base_map)

            return base_map_div
        
        self.generate_map_children(url=self.url, attribution=self.attribuition)



    def __call__(self) -> Any:
        
        return self.pipeline()