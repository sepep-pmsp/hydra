

functions.columns_bullet_list(
    title_bullet_list = "Desagregado por", 
    itens=unidades_list)

sum_mun = distrito['pop_total'].sum()

st.markdown("<h5>Total do Município</h5>", unsafe_allow_html=True)
st.subheader(f'{sum_mun:,} pessoas'.replace(",", "."))

choice_unidade = st.selectbox("", unidades_df['name'])


name_gdf_unidade= find_gdf_info(unidades_df, choice_unidade, 'gdf_name')
name_column_unidade= find_gdf_info(unidades_df, choice_unidade, 'column_name')

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

