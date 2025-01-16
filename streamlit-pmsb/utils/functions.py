import folium
import streamlit as st
from streamlit_folium import st_folium


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

def columns_bullet_list(title_bullet_list, itens):
    st.markdown(f"<h5>{title_bullet_list}</h5>", unsafe_allow_html=True)

    cols = st.columns(len(itens))  
    for a, item in enumerate(itens):
        col = cols[a]  
        with col:
            st.markdown(
                f"""<p >
                    <strong>
                        {a + 1}. {item[0]}
                    </strong>
                    <br> 
                    <div class = "description-bullet-list">{item[1]}</div>
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

def find_gdf_info(unidades_df, choice_unidade, info):    
    unidades_df[unidades_df['name']==choice_unidade][info].values[0]







