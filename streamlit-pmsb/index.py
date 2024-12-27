import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import st_folium
from os.path import join
from utils import (functions, create_sidebar)

#page config
st.set_page_config(
    page_title="Dados de Saneamento em São Paulo", 
    page_icon=None,
    layout= "wide") #ou center

#Read css
with open("styles.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

# Dados
distrito = gpd.read_file(join("data", "2024_11_26", "03_consumo_distrito"))
subbac = gpd.read_file(join("data", "2024_11_26", "03_consumo_subbac"))
subpref = gpd.read_file(join("data", "2024_11_26", "03_consumo_subprefeitura"))
fcu = gpd.read_file(join("data", "2024_11_26", "pop_fcu"))


unidades_list = [
    ("Subprefeituras", "Lorem ipsum dolor sit amet...", 'subpref', 'nm_subpref'),
    ("Distritos", "Lorem ipsum dolor sit amet...", 'distrito', 'nm_distrit'),
    ("Favelas e Comunidades Urbanas", "Lorem ipsum dolor sit amet...", 'fcu', 'nm_fcu'),
    ("Sub Bacias Hidrográficas", "Lorem ipsum dolor sit amet...", 'subbac', 'nm_bacia_h')
]
unidades = pd.DataFrame(unidades_list, columns=['name', 'desc', 'gdf_name', 'column_name'])






# Cabeçalho

container1_header = st.container(border=False, key="container1_header")
path_img = join("img", "img-init-streamlit.svg")
container1_header.image(path_img)
container1_header.text("""Análise de dados referente ao Plano Municipal de Saneamento 2024""")

container2_header = st.container(border=False, key="container2_header")
container2_header.title("Dados de Abastecimento de Água")
container2_header.subheader("Metodologia de análise dos dados | PMSB 2024 | CODATA")
container2_header.text("Este material tem por objetivo registrar a metodologia referente ao processamento de dados elaborado por Codata para a elaboração do diagnóstico do Plano Municipal de Saneamento Básico (2024/2025). Nesse sentido, ele deve ser resultado de um processo enquanto as análises estão sendo realizadas.")

create_sidebar.sidebar_created()

# 1: Cálculo populacional e de domicílios com base no Censo 2022
functions.title_numbered_blue_dot(num = 1, title_name = "Cálculo populacional e de domicílios com base no Censo 2022")


functions.columns_bullet_list(
    title_bullet_list = "Desagregado por", 
    itens=unidades_list)



sum_mun = distrito['pop_total'].sum()
st.markdown("<h5>Total do Município</h5>", unsafe_allow_html=True)
st.subheader(f'{sum_mun:,} pessoas'.replace(",", "."))

choice_unidade = st.selectbox("", unidades['name'])

name_gdf_unidade= (
    unidades[unidades['name']==choice_unidade]
    ['gdf_name']
    .values[0]
)
name_column_unidade= (
    unidades[unidades['name']==choice_unidade]
    ['column_name']
    .values[0]
)
gdf_unidade = locals()[name_gdf_unidade]

choice_name = st.selectbox(
    "", 
    gdf_unidade[name_column_unidade], 
    index=None, 
    placeholder= "Escolha uma unidade..."
    )

if name_gdf_unidade == 'fcu':
        pop_column = 'pop_fcu'
else:
        pop_column = 'pop_total'
if choice_name !=None:
    sum_unidade = (
            gdf_unidade[
                gdf_unidade[name_column_unidade]==choice_name
            ]
            [pop_column]
            .values[0]
        )
else:
    sum_unidade = gdf_unidade[pop_column].sum()
    if name_gdf_unidade == 'subpref':
        sum_unidade = sum_unidade+2

st.subheader(f'{sum_unidade:,} pessoas'.replace(",", "."))


columns_names ={
    name_column_unidade : 'Unidade',
    pop_column: 'População'
}
cols_b1, cols_b2 = st.columns(2)
with cols_b1:
    lat_lon_unidade = functions.find_lat_lon(gdf=gdf_unidade)
    m = folium.Map(
        tiles = "Cartodb Positron",
        zoom_control=True,
        scrollWheelZoom = True,
        dragging = True
        )
    
    gdf_unidade.explore(
        m = m,
        color= '#0D04FF',
        tooltip=list(columns_names.keys()),
        tooltip_kwds={
            'aliases': list(columns_names.values()),
            'localize': True
        },
        popup=list(columns_names.keys()),
        popup_kwds={
            'aliases': list(columns_names.values()),
            'localize': True
        }
    )
    #transformar em função e passar todos os mapas pra um arquivo maps.py
    if choice_name !=None:
        name_unidade = lat_lon_unidade[lat_lon_unidade[name_column_unidade]==choice_name]


        if not name_unidade.empty:
            lat = name_unidade.iloc[0]['lat']
            lon = name_unidade.iloc[0]['lon']

            folium.Marker(
                location=[lat, lon],
                icon=folium.Icon(color="white")
                ).add_to(m)

        
        minx, miny, maxx, maxy = name_unidade.to_crs('EPSG:4326').total_bounds
        bounds=[(miny, minx),(maxy, maxx)]
        m.fit_bounds(bounds)

    else:
        minx, miny, maxx, maxy = gdf_unidade.to_crs('EPSG:4326').total_bounds
        bounds=[(miny, minx),(maxy, maxx)]
        m.fit_bounds(bounds)
    
    plot_map = st_folium(m, height=600)
with cols_b2:
    st.dataframe(
        gdf_unidade[
            [name_column_unidade, pop_column]
        ].sort_values(
            by =pop_column,
            ascending = False
        ),
        height=600,
        column_config=columns_names,
        hide_index=True
    )

functions.popover_metodologia(
    name_popover = "Metodologia Completa de Cálculo de População", 
    metodologia = ("""
        Foram utilizadas as malhas disponíveis em duas bases de dados principais, a do Censo Demográfico de 2022, com as informações agregadas por setores censitários disponibilizada pelo IBGE1; e as das malhas das unidades de desagregação, disponibilizadas pelo GeoSampa2. 
        Para a maior parte das unidades, nós selecionamos apenas os setores censitários que correspondessem ao município de São Paulo, mas para as sub bacias hidrográficas, que não se enquadram na precisão das fronteiras municipais, foram selecionados todos os municípios que tivessem ao menos alguma parte de seu território interseccionando com alguma das sub bacias da malha. 
        Para trabalhar com ambas as malhas, calculamos a similaridade entre elas, e realizamos a intersecção (com o método “overlay intersection” de uma biblioteca do Python chamada GeoPandas). Fizemos o cálculo de cada unidade individualmente, mas o processo permaneceu o mesmo na maioria dos casos. 
        Primeiro, identificamos as áreas de interseção, ou seja, as regiões onde os polígonos dos setores e das unidades se sobrepõe. e fazemos um recorte disso. Ou seja se há um setor que fica dividido pelo contorno de dois ou mais polígonos da unidade, dividiremos esse setor seguindo o contorno da unidade. Contudo, estabelecemos um tamanho mínimo de  10m para essas intersecções, evitando que uma falsa intersecção permanecesse. 
        Calculando a área desses setores antes e após a intersecção, para realizarmos para cada polígono da intersecção o cálculo da porcentagem de área que ela representa do setor total (área da intersecção/área total do setor).
        Para calcular o valor correspondente dos indicadores em cada intersecção, multiplicamos seus valores por sua percentagem da área do setor (valor do indicador total do setor * porcentagem da área do setor que corresponde ao polígono). Assim, é considerado que a variável, seja ela, por exemplo, população ou domicílios, está homogeneamente distribuída no setor e, portanto, a distribuição de seus valores pode ser equivalida à área da intersecção."""),
    obstaculos = (
        """Há uma incompatibilidade entre o limite municipal da malha do IBGE e a do GeoSampa, de forma que ao realizar o cálculo das intersecções alguns setores censitários ficaram para fora, enquanto regiões que deveriam ter setores estavam vazias. Para resolver isso, adicionamos os setores que haviam ficado de fora, independente da razão, manualmente. 
        Nossa metodologia não permite que identifiquemos precisamente a distribuição das variáveis em casos onde elas são distribuídas de forma não homogênea. 
    """
    )
)


# 2. Demanda da População por água
functions.title_numbered_blue_dot(num = 2, title_name = "Demanda da População por água")

functions.columns_bullet_list(
    title_bullet_list = "Desagregado por", 
    itens=unidades_list
)

with st.container(border=True):
    cols_c1, cols_c2 = st.columns(2)
    with cols_c1:
        st.text("Consumo por pessoa")
        st.subheader("140 L/dia")
    with cols_c2:
        st.text("População por setor")
        st.markdown("<h3>População <i>α</i></h3>", unsafe_allow_html=True)
    
    st.text("Demanda estimada por setor")
    st.markdown("<h3>População <i>α</i> X 140</h3>", unsafe_allow_html=True)

st.markdown(
    """<p><strong>Acesso aos materiais</strong></p>
    <ol>
        <li>Shapefiles</li>
        <li>Mapas Interativos</li>
        <li>Notebooks</li>
    </ol>
    """,
    unsafe_allow_html=True)

st.markdown("""
    <p><strong>Fontes de Dados</strong></p>
    <p></p>
    """,
    unsafe_allow_html=True)

#3. Análise da cobertua e distribuição da rede de abastecimento de água
functions.title_numbered_blue_dot(
    num= 3,
    title_name = "Análise da cobertua e distribuição da rede de abastecimento de água"
)

cols_d1, cols_d2 = st.columns(2)
with cols_d1:
    st.markdown("<h5>Desagregado por<h5>", unsafe_allow_html=True)
    st.markdown(
        """
            <ol>
                <li><strong>Subprefeitura</strong></li>
            </ol>
        """, unsafe_allow_html=True
    )
with cols_d2:
    st.markdown("<h5>Resultado por<h5>", unsafe_allow_html=True)
    st.markdown(
        """
            <ol>
                <li><strong>Logradouros cobertos</strong></li>
                <li><strong>Logradouros não cobertos</strong></li>
            </ol>
        """, unsafe_allow_html=True
    )

#st.bar_chart()

functions.popover_metodologia(
    name_popover = "Metodologia Completa de Cálculo", 
    metodologia = ("""
        Foi realizado o cruzamento entre as feições da rede de abastecimento de água e as feições de logradouros oficiais para identificar e quantificar a cobertura de abastecimento de água no município. Os logradouros são entendidos como via de acesso aos imóveis que necessitam de abastecimento de água e foram escolhidos por serem uma base georreferenciada mais precisa do que outras alternativas, como o CNEFE3. 
        Foi aplicado um buffer ao redor das feições da rede de abastecimento para representar a área de cobertura potencial da rede. O buffer aplicado foi de 20 metros, representando aproximadamente uma via de 2 faixas + passeio, considerando que a tubulação pode estar representada em um dos extremos da via, enquanto o próprio logradouro provavelmente estará representado no centro da via.
        Depois, foi calculada a interseção entre as linhas dos logradouros e a geometria da área de cobertura da rede para obtenção dos trechos de logradouro que possuem cobertura (potencial) de abastecimento de água. 
        Finalmente, foi calculada a diferença entre as linhas dos logradouros e a geometria da área de cobertura da rede para obtenção dos trechos de logradouro que não possuem cobertura de abastecimento de água. 
        """),
    obstaculos = (
        """Utilizar a rua/logradouro como unidade de acesso ao domicílio vai contabilizar a ausência de rede mesmo onde não tem domicílio."""
    )
)

st.markdown(
    """<p><strong>Acesso aos materiais</strong></p>
    <ol>
        <li>Shapefiles</li>
        <li>Mapas Interativos</li>
        <li>Notebooks</li>
    </ol>
    """,
    unsafe_allow_html=True)

st.markdown("""
    <p><strong>Fontes de Dados</strong></p>
    <p></p>
    """,
    unsafe_allow_html=True)



