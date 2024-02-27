from dash import (
    Output,
    Input,
    State,
    callback
)
import pandas as pd

from dao import DuckDBDAO
from services import MunicipioService, DistritoService
from etls import SetoresTransformer
from utils import gdf_to_geobuf, load_s3_vars
from dash_bootstrap_templates import ThemeSwitchAIO


from components import (Map,BasicFilter,NavBar,Tab,ThemeSwitch,Table,LayersOffCanvas,initialCardFactory,DetailsCard, BaseLayout)


dao = DuckDBDAO(**load_s3_vars())

@callback(
    Output(Map.SETORES_OVERLAY_ID, 'children'),
    Output(Tab.MESSAGE_TEXT_ID, 'children'),
    Output(Table.COMPONENT_ID, 'rowData'),
    Output(Table.COMPONENT_ID, 'columnDefs'),
    Input(NavBar.FILTER_BUTTON_ID, 'n_clicks'),
    State(BasicFilter.TYPE_SELECT_ID, 'value'),
    State(BasicFilter.COLUMN_SELECT_ID, 'value'),
    State(BasicFilter.OPERATOR_SELECT_ID, 'value'),
    State(BasicFilter.BASIC_VALUE_TEXT_ID, 'value'),
    State(BasicFilter.ADVANCED_VALUE_TEXT_ID, 'value'),
)
def filter_setores(basico_n_clicks, filtro_tipo, filtro_coluna, filtro_operacao, filtro_basico_valor, filtro_avancado_valor):
    print('Filtrando setores...')
    if not (filtro_basico_valor or filtro_avancado_valor):
        setores = SetoresTransformer()
    else:
        if filtro_tipo == 'Avançado':
            filtro = filtro_avancado_valor
        elif filtro_tipo == 'Básico':
            filtro = f'{filtro_coluna} {filtro_operacao} {filtro_basico_valor}'

        setores = SetoresTransformer(
            filtro_personalizado=filtro)

    setor_gdf = setores()
    setor_geobuf = gdf_to_geobuf(setor_gdf)

    coluna_options = [
        col.split(' ')[-1] for col in setores.colunas_selecionadas
    ]

    msg = f"{setor_gdf.shape[0]} setores censitários encontrados com o filtro {filtro}!"
    print(msg)
    print('Retornando setores...')
    setor_gdf = setor_gdf.drop(columns=['geometry', 'tooltip'])
    setor_df = pd.DataFrame(setor_gdf)
    setor_df['id'] = setor_df['codigo_setor']
    dados_setor = setor_df.to_dict('records')

    cols = Table.get_columns(setor_df.columns)

    return Map.setores_overlay_children(setor_geobuf), msg, dados_setor, cols

@callback(
    Output(Map.LIMITE_MUNICIPAL_PANE_ID, 'children'),
    Input(BaseLayout.INITIAL_LOAD_SPAN_ID, 'children')
)
def initial_load(children):
    geobuf = MunicipioService(dao).get_geobuf()
    return Map.limite_municipal_children(geobuf)

def carregar_detalhes_setor(codigo_setor:str):
    setores = SetoresTransformer(filtro_personalizado=f'codigo_setor == {codigo_setor}')
    gdf = setores()
    df = pd.DataFrame(gdf.drop(columns=['geometry','tooltip']))
    df = df.iloc[0]
    setor = df.to_dict()
    setor_geobuf = gdf_to_geobuf(gdf)

    ds = DistritoService(dao)
    
    distrito_gdf = ds.find_by_setor(codigo_setor, format='geodataframe', tooltip_column='nm_distrito_municipal')
    setor['nm_distrito_municipal'] = distrito_gdf['nm_distrito_municipal'].iloc[0]
    setor['nm_distrito_municipal'] = setor['nm_distrito_municipal'].title()

    distrito_geobuf = gdf_to_geobuf(distrito_gdf)

    return (
        DetailsCard.card_detalhes_children(**setor),
        Map.setor_detalhes_overlay_children(setor_geobuf),
        Map.distrito_municipal_children(distrito_geobuf)
    )

@callback(
    Output(DetailsCard.COMPONENT_ID, 'children', allow_duplicate=True),
    Output(Map.SETOR_DETALHES_OVERLAY_ID, 'children', allow_duplicate=True),
    Output(Map.DISTRITOS_PANE_ID, 'children', allow_duplicate=True),
    Input(Table.COMPONENT_ID, 'selectedRows'),
    prevent_initial_call='initial_duplicate'
)
def load_details_from_table(selectedRows):
    if selectedRows:
        selected_row = selectedRows[0]
        print(selected_row)
        return carregar_detalhes_setor(selected_row['codigo_setor'])
    return None, None, None

@callback(
    Output(DetailsCard.COMPONENT_ID, 'children', allow_duplicate=True),
    Output(Map.SETOR_DETALHES_OVERLAY_ID, 'children', allow_duplicate=True),
    Output(Map.DISTRITOS_PANE_ID, 'children', allow_duplicate=True),
    Input(Map.SETORES_GEOJSON_ID, 'click_feature'),
    prevent_initial_call='initial_duplicate'
)
def load_details_from_map(feature):
    if feature:
        print(feature['properties'])
        return carregar_detalhes_setor(feature['properties']['codigo_setor'])
    return None, None, None


@callback(
    Output(Map.DISTRITOS_OVERLAY_ID, 'checked'),
    Input("distrito_municipal_toggle", 'on')
)
def update_checked_layers(value):
    return value

@callback(
    Output(BasicFilter.ADVANCED_FILTER_COLLAPSE_ID, 'is_open'),
    Output(BasicFilter.BASIC_FILTER_COLLAPPSE_ID, 'is_open'),
    Input(BasicFilter.TYPE_SELECT_ID, 'value')
)
def selecionar_filtro(filtro_tipo_value: str) -> tuple[bool, bool]:
    if filtro_tipo_value == 'Básico':
        return False, True
    if filtro_tipo_value == 'Avançado':
        return True, False
@callback(
    Output(Table.COMPONENT_ID, "exportDataAsCsv"),
    Input("csv-button", "n_clicks"),
)
def export_data_as_csv(n_clicks):
    if n_clicks:
        return True
    return False


tyle_layer_theme1 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png'
tyle_layer_theme2 = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
map_constructor = Map()


@callback(
    Output('map', 'children'),
    Input('theme-store', 'data'),
    prevent_initial_call=True
)
def update_tile_layer(theme):
    tyle_layer = tyle_layer_theme1 if theme else tyle_layer_theme2
    url = tyle_layer
    attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

    return map_constructor.generate_map_children(url, attribution)

@callback(
    Output('theme-store', 'data'),
    Input(ThemeSwitchAIO.ids.switch("theme"), 'value'),
    prevent_initial_call=True
)
def update_theme(theme_value):
    
    return theme_value

@callback(
    Output("offcanvas-placement", "is_open"),
    Input("open-offcanvas-placement", "n_clicks"),
    [State("offcanvas-placement", "is_open")],
)
def toggle_offcanvas(n1, is_open):
    if n1:
        return not is_open
    return is_open
