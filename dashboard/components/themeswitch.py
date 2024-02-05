from typing import Any
from dash_bootstrap_templates import ThemeSwitchAIO
import dash_bootstrap_components as dbc
from dash import html

class ThemeSwitch:

    def __init__(self) -> None:
        self.first_theme =  "materia"
        self.second_theme = "cyborg"
        self.first_theme_url = dbc.themes.MATERIA
        self.second_theme_url = dbc.themes.CYBORG

    def generate_theme_switch(self) -> html.Div :
        theme_switch = ThemeSwitchAIO(aio_id="theme", themes=[self.first_theme_url, self.second_theme_url],)
        theme_switch_div = html.Div(theme_switch)

        return theme_switch_div
    
    def pipeline(self) -> html.Div:
        theme_switch_div = self.generate_theme_switch()

        return theme_switch_div
    
    def __call__(self) -> Any:
        
        return self.pipeline()