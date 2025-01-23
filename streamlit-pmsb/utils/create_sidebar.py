import streamlit as st

def sidebar_created():
    with st.sidebar:
        st.header("Dados de Saneamento em São Paulo")
        st.write("""Os dados aqui expostos foram trabalhados na Secretaria Executiva de Planejamento e Entregas Prioritárias (SEPEP), em uma colaboração entre a Cordenadoria de Tecnologia e Dados (CODATA) e a Coordenadoria de Segurança Hídrica (COSH), em que a primeira se comprometia a utilizar dados abertos para desenvolver mapas e tabelas segundo as demandas da equipe da segunda para o desenvolvimento do Plano Municipal de Saneamento Básico (PMSB).
                \n **O PMSB aborda o saneamento básico como base para a construção de Saúde Única e Desenvolvimento Sustentável no município de São Paulo, fortalecendo continuamente a Segurança Hídrica municipal. Com isso, o Plano busca assegurar, para além da universalização, a melhoria contínua de aspectos de equidade, eficiência dos serviços, sustentabilidade transparência, mitigação e adaptação climática.**
                 \n *(Plano Municipal de Saneamento Básico - Diagnóstico Preliminar, 2024)*
                \n \n 
    """)
        

