from typing import List

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

TOP_N = 50  # number of vectors which are the most similar to user vector, value can be changed


def model(
    adjacency_matrix: pd.DataFrame, most_popular_index: List[int], user_pk: int
) -> List[int]:
    user_vec = adjacency_matrix[adjacency_matrix["user_id"] == user_pk]
    # TODO: удалить перед выкаткой в прод
    if len(user_vec) == 0:
        raise ValueError(f"Can't find user with id {user_pk}")
    if len(user_vec) != 0:
        adjacency_matrix = adjacency_matrix.drop(user_vec.index)
        adjacency_matrix = adjacency_matrix.drop("user_id", axis=1)
        user_tried_wines = user_vec.dropna(axis=1).drop("user_id", axis=1)
        adjacency_matrix_crop = adjacency_matrix[user_tried_wines.columns].dropna(
            how="all"
        )

        adjacency_matrix_crop = adjacency_matrix_crop.fillna(0.5)
        adjacency_matrix_crop = adjacency_matrix_crop.applymap(lambda x: x * 2 - 1)
        user_tried_wines = user_tried_wines.applymap(lambda x: x * 2 - 1)

        similarity = cosine_similarity(user_tried_wines, adjacency_matrix_crop)
        similar_users = np.argsort(similarity[0])
        similar_users = similar_users[::-1][:TOP_N]
        similar_users_index = adjacency_matrix_crop.index[similar_users]

        wine_recommended_sum = adjacency_matrix.iloc[similar_users_index].sum(axis=0)
        wine_recommended_sum = wine_recommended_sum[wine_recommended_sum > 0]

        recommended_wines_sorted = np.argsort(wine_recommended_sum)
        recommended_wines_sorted_index = wine_recommended_sum.index[
            recommended_wines_sorted
        ]

        recommended_wines_sorted_index = [
            wine
            for wine in recommended_wines_sorted_index
            if wine not in user_tried_wines.columns
        ]
    else:
        recommended_wines_sorted_index = []

    most_popular_index = list(
        filter(lambda x: x not in recommended_wines_sorted_index, most_popular_index)
    )

    return recommended_wines_sorted_index + most_popular_index
