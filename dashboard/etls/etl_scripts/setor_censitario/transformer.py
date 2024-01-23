import json
import dash_leaflet.express as dlx

from ..base_transformer import BaseTransformer


class Transformer(BaseTransformer):
    def __init__(self, filtro_personalizado: str = None):
        colunas = [
            'cd_original_setor_censitario AS codigo_setor',
            'Domicilio01_SP1_V002 AS qtd_domicilios',
            'Domicilio01_SP1_V012 AS qtd_domicilios_rede_geral',
            'Domicilio01_SP1_V019 AS qtd_domicilios_fossa_rudimentar',
            'Domicilio01_SP1_V021 AS qtd_domicilios_esgotamento_rio',
            'geometry'
        ]

        super().__init__(
            nome_da_camada='setor_censitario_enriched',
            tooltip_text='codigo_setor',
            colunas=colunas,
            filtro_personalizado=filtro_personalizado,
            lazy_loading=True
        )

    def filtrar_resultado_por_distrito(self, random_dist, duckdb_relation):
        duckdb_relation = duckdb_relation.filter(
            f'cd_identificador_distrito == {random_dist["cd_identificador_distrito"].iloc[0]}')

        return duckdb_relation

    def pipeline(self):

        duckdb_relation = self.filtrar_colunas(self.package)
        if self.filtro_personalizado:
            duckdb_relation = self.filtrar_personalizado(duckdb_relation)
        geodataframe_setores_por_distrito = self.transformar_geodataframe(
            duckdb_relation)
        geojson = json.loads(geodataframe_setores_por_distrito.to_json())
        geobuf_setores_por_distrito = dlx.geojson_to_geobuf(geojson)

        return geobuf_setores_por_distrito

    def __call__(self):
        return self.pipeline()
