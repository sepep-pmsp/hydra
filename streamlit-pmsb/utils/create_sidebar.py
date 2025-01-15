import streamlit as st

def sidebar_created():
    with st.sidebar:
        st.header("Dados de Saneamento em São Paulo")
        navigation_radio = st.radio(
            "Navegação",
            ["Dados de abastecimento de Água", "Dados de cobertura de esgoto"]
        )
        st.write("""
                Este material tem por objetivo registrar a metodologia referente ao processamento de dados elaborado por Codata para a elaboração do diagnóstico do Plano Municipal de Saneamento Básico (2024/2025). Nesse sentido, ele deve ser resultado de um processo enquanto as análises estão sendo realizadas.
                \n **O PMSB aborda o saneamento básico como base para a construção de Saúde Única e Desenvolvimento Sustentável no município de São Paulo, fortalecendo continuamente a Segurança Hídrica municipal. Com isso, o Plano busca assegurar, para além da universalização, a melhoria contínua de aspectos de equidade, eficiência dos serviços, sustentabilidade transparência, mitigação e adaptação climática.**
                 \n *(Plano Municipal de Saneamento Básico - Diagnóstico Preliminar, 2024)*
    """)
        

