import folium
import streamlit as st
from streamlit_folium import st_folium
from utils import gdf_operations




def title_numbered_blue_dot(num, title_name):
    col_bd1, col_bd2 =st.columns([0.2, 0.7])

    with col_bd1:
        st.markdown(f"""
            <p class = "li-blue-dot">
                <div class = "blue-dot">{num}.</div>""", 
            unsafe_allow_html=True)
    with col_bd2:
        st.markdown(f"""
            <p class = "li-blue-dot">
                <div class = "title-blue-dot">{title_name}</div>""", 
            unsafe_allow_html=True)
    #arrumar essa partezinha
    st.container(height= 2, border=False)

def columns_bullet_list(
    title_bullet_list, 
    itens, 
    gdf_unidade, 
    name_gdf_unidade, 
    choice_unidade, 
    choice_name
    ):
    
    cd_column_unidade = gdf_operations.find_gdf_name(
        gdf_unidade, 
        name_gdf_unidade, 
        'cd_'
    )
    nm_column_unidade = gdf_operations.find_gdf_name(
        gdf_unidade,
        name_gdf_unidade,
        'nm_'
    )


    gdf_intersec = gdf_operations.intersec_unidades(
        itens,
        gdf_unidade,
        name_gdf_unidade
    )

    index_unidade = (
        itens[
            itens['gdf_name'] == name_gdf_unidade
        ].index[0]
    )

    st.markdown(f"<h5>{title_bullet_list}</h5>", unsafe_allow_html=True)
    
    cols = st.columns(len(itens))  
    for index, item in itens.iterrows():
        desc= ''

        if index<= index_unidade:
            name_intersec = item.loc['gdf_name']
            cd_column_intersec = item.loc['column_cd']
            nm_column_intersec = item.loc['column_name']
            nm_column_intersec
            

            gdf_outro = gdf_operations.get_dados(name_intersec)
            
            if choice_name != None:
                gdf_outro[cd_column_intersec] = (
                    gdf_outro[cd_column_intersec]
                    .astype(int)
                    .astype(str)
                )

                mapper_name = dict(
                    zip(
                        gdf_outro[cd_column_intersec], 
                        gdf_outro[nm_column_intersec]
                    ))
                
                gdf_intersec[nm_column_intersec] = (
                gdf_intersec[cd_column_intersec]
                .map(mapper_name)
                )


                
                desc = gdf_intersec[gdf_intersec[nm_column_unidade]==choice_name] [nm_column_intersec].iloc[0]
    
        col = cols[index]  

        with col:
            st.markdown(
                f"""<p >
                    <strong>
                        {item['name']}
                    </strong>
                    <br> 
                    <div class = "description-bullet-list">{desc}</div>
                </p>""",
                unsafe_allow_html=True
            )

def popover_metodologia(name_popover, metodologia, obstaculos):
    lines = [line for line in metodologia.splitlines() if line.strip()]
    with st.popover(name_popover):
        st.subheader(name_popover)
        st.markdown(
            "<ol>" 
            + ""
            .join(
                [f"<li>{line}</li>" for line in lines]
            ) 
            + 
            "</ol>", 
            unsafe_allow_html=True
        )

        st.subheader("Obstáculos")
        st.text(obstaculos)

def find_lat_lon(gdf):
    for index, row in gdf.iterrows():
        centroid = row['geometry'].centroid
        gdf.at[index, 'lat'] = centroid.y
        gdf.at[index, 'lon'] = centroid.x
    return gdf

def find_gdf_info(unidades_df, choice_unidade, column_info, return_info):  #passar pra gdf_operations ou trazer find name pra cá  
    print(column_info)
    print(choice_unidade)
    print(return_info)
    unidades_df[unidades_df[column_info]==choice_unidade][return_info].values[0]
    







