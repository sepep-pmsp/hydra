# Hydra

⠄⠄⣴⣶⣤⡤⠦⣤⣀⣤⠆⠄⠄⠄⠄⠄⣈⣭⣭⣿⣶⣿⣦⣼⣆⠄⠄⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠉⠻⢿⣿⠿⣿⣿⣶⣦⠤⠄⡠⢾⣿⣿⡿⠋⠉⠉⠻⣿⣿⡛⣦⠄⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠈⠄⠄⠄⠈⢿⣿⣟⠦⠄⣾⣿⣿⣷⠄⠄⠄⠄⠻⠿⢿⣿⣧⣄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠄⠄⠄⣸⣿⣿⢧⠄⢻⠻⣿⣿⣷⣄⣀⠄⠢⣀⡀⠈⠙⠿⠄⠄⠄⠄
⠄⠄⢀⠄⠄⠄⠄⠄⠄⢠⣿⣿⣿⠈⠄⠄⠡⠌⣻⣿⣿⣿⣿⣿⣿⣿⣛⣳⣤⣀⣀⠄⠄
⠄⠄⢠⣧⣶⣥⡤⢄⠄⣸⣿⣿⠘⠄⠄⢀⣴⣿⣿⡿⠛⣿⣿⣧⠈⢿⠿⠟⠛⠻⠿⠄⠄
⠄⣰⣿⣿⠛⠻⣿⣿⡦⢹⣿⣷⠄⠄⠄⢊⣿⣿⡏⠄⠄⢸⣿⣿⡇⠄⢀⣠⣄⣾⠄⠄⠄
⣠⣿⠿⠛⠄⢀⣿⣿⣷⠘⢿⣿⣦⡀⠄⢸⢿⣿⣿⣄⠄⣸⣿⣿⡇⣪⣿⡿⠿⣿⣷⡄⠄
⠙⠃⠄⠄⠄⣼⣿⡟⠌⠄⠈⠻⣿⣿⣦⣌⡇⠻⣿⣿⣷⣿⣿⣿⠐⣿⣿⡇⠄⠛⠻⢷⣄
⠄⠄⠄⠄⠄⢻⣿⣿⣄⠄⠄⠄⠈⠻⣿⣿⣿⣷⣿⣿⣿⣿⣿⡟⠄⠫⢿⣿⡆⠄⠄⠄⠁
⠄⠄⠄⠄⠄⠄⠻⣿⣿⣿⣿⣶⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⡟⢀⣀⣤⣾⡿⠃⠄⠄⠄⠄
⠄⠄⠄⠄⢰⣶⠄⠄⣶⠄⢶⣆⢀⣶⠂⣶⡶⠶⣦⡄⢰⣶⠶⢶⣦⠄⠄⣴⣶⠄⠄⠄⠄
⠄⠄⠄⠄⢸⣿⠶⠶⣿⠄⠈⢻⣿⠁⠄⣿⡇⠄⢸⣿⢸⣿⢶⣾⠏⠄⣸⣟⣹⣧⠄⠄⠄
⠄⠄⠄⠄⠸⠿⠄⠄⠿⠄⠄⠸⠿⠄⠄⠿⠷⠶⠿⠃⠸⠿⠄⠙⠷⠤⠿⠉⠉⠿⠆⠄⠄

Bem-vindo ao repositório do Hydra, um **projeto de Servidor de Dados Georreferenciados sobre Saneamento e Hidrografia - Município de São Paulo** 🌊🗺️

Este projeto utiliza uma combinação de ferramentas, incluindo Dagster, MinIO, Postgres e PostGIS, para coletar, processar e armazenar informações hidrográficas em uma arquitetura Docker Compose. Abaixo estão os detalhes essenciais para começar:

### Visão Geral

Este projeto visa criar um ambiente robusto para coleta, conformação, armazenamento e processamento de dados sobre saneamento e hidrografia do município de São Paulo, permitindo análises geoespaciais avançadas.

### Ferramentas Utilizadas

- **Dagster**: Orquestração de fluxos de dados.
- **MinIO**: Armazenamento de dados brutos e conformados em buckets separados.
- **Postgres**: Armazenamento de dados estruturados.
- **PostGIS**: Processamento de dados georreferenciados.

### Estrutura do Diretório

- `docker-compose.dev.yml`: arquivo compose do ambiente de desenvolvimento;
- `docker-compose.hom.yml`: arquivo compose do ambiente de homologação;
- `docker-compose.prod.yml`: arquivo compose do ambiente de produção;
- `README.md`: Este arquivo.

### Configuração do Ambiente

1. **Pré-requisitos**: Certifique-se de ter o Docker e o Docker Compose instalados em sua máquina.

2. **Clonar o Repositório**: Clone este repositório para o seu ambiente local.

3. **Configurar Variáveis de Ambiente**: Renomeie o arquivo `.env.example` para `.env` e configure as variáveis de ambiente necessárias, como chaves do MinIO, informações do banco de dados Postgres, etc.

4. **Iniciar os Contêineres**: Navegue até o diretório `/docker-compose` e execute o seguinte comando para iniciar os contêineres:

   ```bash
   docker-compose -f [arquivo do ambiente escolhido] up -d
   ```
   
### Acesso aos Serviços

- **Dagster**: Acesse a interface do Dagster em `http://localhost:3000`.
- **MinIO**: O MinIO estará disponível em `http://localhost:9000`, onde você pode acessar os buckets de dados.
- **Postgres/PostGIS**: Configure suas ferramentas de gerenciamento de banco de dados para se conectar à instância Postgres, usando as credenciais fornecidas no arquivo `.env`.

Se você tiver dúvidas ou precisar de ajuda, fique à vontade para criar uma **Issue** neste repositório. 🚀🌊🗺️
