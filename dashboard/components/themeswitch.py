from typing import Any
from dash_bootstrap_templates import ThemeSwitchAIO
import dash_bootstrap_components as dbc
from dash import html, dcc
class ThemeSwitch:
    STORE_THEME_ID = 'theme-store'

    def __init__(self) -> None:
        self.class_names = 'theme_switch_div'
        self.first_theme =  "materia"
        self.second_theme = "cyborg"
        self.first_theme_url = dbc.themes.CERULEAN
        self.second_theme_url = dbc.themes.DARKLY

    def generate_theme_switch(self) -> html.Div :
        theme_switch = ThemeSwitchAIO(aio_id="theme", themes=[self.first_theme_url, self.second_theme_url],)
        store_theme_div = html.Div(dcc.Store(id=ThemeSwitch.STORE_THEME_ID, storage_type='memory', data='theme1'))

        theme_switch_div = html.Div(className= self.class_names , children=[theme_switch, store_theme_div])

        return theme_switch_div
    
    def pipeline(self) -> html.Div:
        theme_switch_div = self.generate_theme_switch()

        return theme_switch_div
    
    def __call__(self) -> Any:
        
        return self.pipeline()