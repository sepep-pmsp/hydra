import streamlit as st
import geopandas as gpd
import pandas as pd
import plotly.express as px 
import folium
from streamlit_folium import st_folium
from os.path import join
from utils import (functions, create_sidebar, gdf_operations)



#page config

favicon = join("img", "logotipo_prefeitura", "LOGO PREFEITURA", "LOGOTIPO_PREFEITURA_CENTRALIZADO_FUNDO_ESCURO.png")
st.set_page_config(
    page_title="Dados de Saneamento em São Paulo", 
    page_icon=favicon,
    layout= "wide") #wide ou centered

#Read css
with open("styles.css") as f:
    st.markdown(
        f"<style>{f.read()}</style>",
        unsafe_allow_html=True
    )

#import icons
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css">', unsafe_allow_html=True)

# Dados
distrito = gdf_operations.get_dados('distrito')
subbac = gdf_operations.get_dados('subbac')
subpref = gdf_operations.get_dados('subpref')
fcu = gdf_operations.get_dados('fcu')


unidades_df = gdf_operations.listing_unidades(subbac)
gdf_intersec = gpd.GeoDataFrame()






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
st.text("Total estimado da população do município por níveis de desagregação, calculado a partir do processo de interseção entre dados abertos. As principais fontes de foram o GeoSampa e o IBGE, em especial os setores censitários do censo de 2022.")


functions.popover_metodologia(
    name_popover = "Metodologia Completa de Cálculo de População", 
    metodologia = ("""
        Foram utilizadas as malhas disponíveis em duas bases de dados principais, a do Censo Demográfico de 2022, com as informações agregadas por setores censitários disponibilizada pelo IBGE1; e as das malhas das unidades de desagregação, disponibilizadas pelo GeoSampa. 
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

bullet_list_container = st.container(border=False)





sum_mun = distrito['pop_total'].sum()
st.markdown("<h5>Total do Município</h5>", unsafe_allow_html=True)
st.subheader(f'{sum_mun:,} pessoas'.replace(",", "."))

choice_unidade = st.selectbox("", unidades_df['name'])

name_gdf_unidade= (
    unidades_df[unidades_df['name']==choice_unidade]
    ['gdf_name']
    .values[0]
)
name_column_unidade= (
    unidades_df[unidades_df['name']==choice_unidade]
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
    unidades_df['teste'] = unidades_df['name']
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

bullet_list_container.write(functions.columns_bullet_list(
    title_bullet_list = "Níveis de Desagregação:", 
    itens=unidades_df,
    gdf_unidade=gdf_unidade,
    name_gdf_unidade = name_gdf_unidade,
    choice_unidade=choice_unidade,
    choice_name=choice_name
))

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





# 2. Demanda da População por água
functions.title_numbered_blue_dot(num = 2, title_name = "Demanda da População por água")

#functions.columns_bullet_list(title_bullet_list = "Desagregado por", itens=unidades_df)
st.text("A partir dos resultados do cálculo da população, calculou-se a estimativa de demanda por água, considerando o consumo médio de 140 L/dia para cada pessoa.")

with st.container(border=True, key="container_section2"):
    cols_c1, cols_c2, cols_c3 = st.columns([0.45, 0.10 ,0.45], vertical_alignment='top')
    with cols_c1:
        st.text("Consumo por pessoa")
        st.subheader("140 L/dia")
    with cols_c3:
        st.text("População por setor")
        st.markdown("<h3>População <i>α</i></h3>", unsafe_allow_html=True)
    
    cols_d1, cols_d2, cols_d3= st.columns([0.25, 0.5, 0.25], vertical_alignment='bottom')
    with cols_d2:
        st.text("Demanda estimada por setor")
        st.markdown("<h3>População <i>α</i> X 140</h3>", unsafe_allow_html=True)
st.subheader("Consumo Estimado de Água por Distrito")
container_barchart = st.container(height=507, border=False)
container_barchart.bar_chart(
            data=distrito.sort_values('consumo_di', ascending=True), 
            y='consumo_di', 
            x='nm_distrit', 
            x_label='Cosumo Estimado', 
            y_label='Distrito', 
            color='consumo_di',
            horizontal=True, 
            stack=True, 
            height=None)







st.markdown(
    """<p><strong>Acesso aos materiais</strong></p>
    <ol>
        <li> <a href='https://cloudprodamazhotmail.sharepoint.com/:f:/s/SGM-SEPEP-COSH/EoJ_pB1pOudFjeI_GAlXSDEBHqh-TEqU88wY9d886qdqlQ?e=OL1E8L'>Notebooks <i class="fa-solid fa-laptop-code"></i></li></a>
        <li><a href='https://github.com/sepep-pmsp/bases-pmsb'> Repositório Git Hub <i class="fa-brands fa-github"></i></a></li>
        <li><a href="https://cloudprodamazhotmail.sharepoint.com/:f:/s/SGM-SEPEP-COSH/En8cA87L3ZtHrG8cXEaZ5R4Byp7OuBlR8AOkRLPvVoeneg?e=Q7EO4i">Shapefiles <i class="fa-solid fa-folder-open"></i></li></a>
        <li><a href="https://cloudprodamazhotmail.sharepoint.com/:f:/s/SGM-SEPEP-COSH/EivPwcB0bBRFqs-r_xAwMh0Bz9bTEwTV6NFT_qcvr9NdUg?e=zqsRB8">Mapas Interativos <i class="fa-solid fa-globe"></i></li></a>
    </ol>
    """,
    unsafe_allow_html=True)

st.markdown("""
    <!--<p><strong>Fontes de Dados</strong></p>
    <p></p>-->
    """,
    unsafe_allow_html=True)



