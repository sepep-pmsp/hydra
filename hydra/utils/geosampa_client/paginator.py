import warnings

from .base_client import BaseClient
from .exceptions import PaginationError


class Paginator:
    def __init__(self, get_function: BaseClient, schemas: dict = None) -> None:
        self.schemas = schemas or {}
        self.get = get_function

    def extract_total_features(self, resp: dict) -> int:
        return resp["totalFeatures"]

    def extract_returned_quantity(self, resp: dict) -> int:
        return len(resp["features"])

    def needs_pagination(self, total_features: int, returned_quantity: int) -> bool:
        return total_features > returned_quantity

    def get_steps(self, total_features: int, returned_quantity: int) -> list:
        # need to start at zero because first query wans't ordered
        return [step for step in range(0, total_features, returned_quantity)]

    def warn_steps(self, feature_name: str, steps: list) -> None:
        total_steps = len(steps)

        warnings.warn(f"Paginação iniciada. Serão realizadas {total_steps} requisições para a {feature_name}")

    def get_index_col(self, feature_name: str, index_col: str = None) -> str:
        if index_col:
            warnings.warn(f"Certifique-se que a index_col de fato é uma coluna existente na feature")
            return index_col

        if not self.schemas:
            raise ValueError(f"Must set schemas if willing to paginate and not specify index col")

        feature_schemas = self.schemas.get(feature_name, None)
        if feature_schemas is None:
            raise ValueError(f"Schema for feature {feature_name} not found. Must specify index col")

        index_col = feature_schemas.get("id_col")
        if index_col is None:
            raise ValueError(f"Feature {feature_name} has no defaul index col. Must specify index col")

        return index_col

    def paginate(self, feature_name: str, resp: dict, index_col: str = None, *_ignored, **query_params) -> dict:
        total_features = self.extract_total_features(resp)
        returned_quantity = self.extract_returned_quantity(resp)

        if not self.needs_pagination(total_features, returned_quantity):
            return resp

        print("Paginação iniciada")
        index_col = self.get_index_col(feature_name, index_col)

        steps = self.get_steps(total_features, returned_quantity)
        self.warn_steps(feature_name, steps)

        # recriando as features
        resp["features"] = []

        for _ in steps:
            resp_step = self.get("GetFeature", typeName=feature_name, sortBy=index_col, **query_params)
            features_step = resp_step["features"]
            resp["features"].extend(features_step)
            max_index = features_step[-1]["properties"][index_col]
            query_params["cql_filter"] = f"{index_col}>{max_index}"

        total_returned_features = len(resp["features"])
        if not total_returned_features == total_features:
            raise PaginationError(
                f"""Difference in total features and paginated features: 
                          total - {total_features} vs returned - {total_returned_features}
                          """
            )

        return resp

    def __call__(self, feature_name: str, resp: dict, index_col: str = None, *_ignored, **query_params) -> dict:
        return self.paginate(feature_name, resp, index_col, **query_params)
