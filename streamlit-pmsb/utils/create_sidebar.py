import streamlit as st

def sidebar_created():
    with st.sidebar:
        st.header("Dados de Saneamento em São Paulo")
        navigation_radio = st.radio(
            "Navegação",
            ["Dados de abastecimento de Água", "Dados de cobertura de esgoto"]
        )
        st.text("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aliquam ac dolor malesuada, molestie leo ac, vulputate erat. Nulla ultrices suscipit leo rhoncus consequat. Cras bibendum eros vitae ipsum accumsan tristique et at justo. Donec vitae dapibus urna. Suspendisse iaculis odio et eros suscipit maximus ac ac lacus. Mauris euismod eleifend finibus. Morbi dapibus euismod erat, sed semper augue suscipit ullamcorper. Nullam aliquam eu mi sit amet tincidunt. Maecenas ac augue urna. Mauris sagittis lacus tellus, cursus dictum justo hendrerit ut. Suspendisse sapien ex, tincidunt eget lectus nec, aliquet pulvinar purus. Vivamus augue sem, dignissim vel feugiat sed, luctus ac mauris. Etiam viverra porttitor ultrices. Cras nec suscipit erat, a lobortis nisl. Cras  Vivamus augue sem")

