from typing import Any
import dash_bootstrap_components as dbc
from dash import html
import dash_leaflet as dl




class Map:

    def __init__(self, 
                 url:str = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png', 
                 attribution:str = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> ',
                 callback_load_children:bool = False) -> None:
        
        self.callback_load_children = callback_load_children
        self.url = url
        self.attribuition = attribution
        
        
        self.style = {'height': '80vh'}
        self.classNames = 'map'
        self.id = 'map'
        self.center = [-23.5475, -46.6375]
        self.zoom = 10


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
            dl.Overlay(dl.Pane(children=[],
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
            dl.Overlay(children=[],
                        id="setores_ol",
                        name='setores_ol',
                        checked=True
                        )
        )


        overlay.append(
            dl.Overlay(children=[],
                        id="setor_detalhes_ol",
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
                id=self.id,
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