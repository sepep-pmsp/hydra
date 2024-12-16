from typing import Any
import dash_bootstrap_components as dbc
from dash import html
import dash_daq as daq




class LayersOffCanvas:
    
    OPEN_LAYERS_BUTTON_ID = 'open-offcanvas-placement'
    OFFCANVAS_ID = 'offcanvas-placement'


    def __init__(self) -> None:
        

        
        self.class_names = {"on_off_layer_button" : "",
                            "offcanvas" : "",
                            "layer_title":"",
                            "layer_toggle":"layer_toggle_div",
                            "layer" : "layer_div"}
        
        
        self.ids = {"on_off_layer_button": LayersOffCanvas.OPEN_LAYERS_BUTTON_ID,
                    "offcanvas": LayersOffCanvas.OFFCANVAS_ID}
        
        
        self.placement = "start"
        
        self.offcanvas_title = "Camadas"
        
        self.offcanvas_layers = ["area_contaminada_reabilitada_svma", "area_inundavel", "distrito_municipal", "GEOSAMPA_cadparcs_area_protecao_apa", "manancial_billings", "manancial_guarapiranga", "manancial_juquery","remanescente_pmma","represa_nivel_maximo","risco_ocorrencia_alagamento", "risco_ocorrencia_inundacao", "setor_censitario_2010", "subprefeitura", "transpetro_duto"]
        
        self.offcanvas_text = "Ative ou desative livremente as camadas que deseja visualizar no mapa:"
                
        
            
        

    def generate_offcanvas_button(self) -> html.Div :
        on_off_layer_button = dbc.Button(
            "Camadas", 
            id=self.ids.get("on_off_layer_button"), 
            class_name=self.class_names.get("on_off_layer_button"),
            n_clicks=0
        )

        return html.Div(on_off_layer_button)
    
    def generate_offcanvas_options(self) -> html.Div:
        layers = []

        for layer in self.offcanvas_layers:
            title = html.H6(layer, id="{}_title".format(layer),
                                    className=self.class_names.get("layer_title"))

            button = daq.BooleanSwitch(
                id="{}_toggle".format(layer),
                label="Exibir no mapa:",
                on=False,
                className=self.class_names.get("layer_toggle"),
                )
            
            layer_div = html.Div([title, button], className=self.class_names.get("layer"))
            
            layers.append(layer_div)
            
        return html.Div(layers)
    
    def generate_offcanvas(self,offcanvas_options) -> html.Div :
        offcanvas = html.Div(
    [
        dbc.Offcanvas(
            [html.P(self.offcanvas_text), offcanvas_options],
            id=self.ids.get("offcanvas"),
            class_name=self.class_names.get("offcanvas"),
            title=self.offcanvas_title,
            is_open=False,
            placement=self.placement
        ),
    ]
)
        return offcanvas
    

                
            
    
    def pipeline(self) -> Any:

        offcanvas_button  = self.generate_offcanvas_button()
        offcanvas_options = self.generate_offcanvas_options()
        offcanvas = self.generate_offcanvas(offcanvas_options)

        return [offcanvas,offcanvas_button]
    
    def __call__(self) -> Any:
        
        return self.pipeline()