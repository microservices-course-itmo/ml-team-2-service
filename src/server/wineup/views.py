import os
import subprocess
from typing import List
import json
import logging
import math

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Wine, User, Review
from .serializers import (
    WineSerializer,
    UserSerializer,
    ReviewSerializer,
    ReviewModelSerializer,
)
from tqdm import tqdm
import pandas as pd
import numpy as np
from .recommendation_model import model
from .jobs.user_sync import user_sync_job
from .jobs.favorites_sync import favorites_sync_job
from threading import Thread

logger = logging.getLogger(__name__)


def build_adjacency_matrix() -> pd.DataFrame:
    print("Start building adjacency matrix")
    users = User.objects.exclude(internal_id__isnull=True).all()
    wines = Wine.objects.exclude(internal_id__isnull=True).order_by("pk").all()
    wine_pk_wine_id = dict(zip([wine.pk for wine in wines], range(len(wines))))
    adjacency_matrix = []
    for user in tqdm(users):
        user_reviews = Review.objects.filter(user_id=user.pk)
        result = [int(user.pk)] + [None] * len(wines)
        for review in user_reviews:
            result[wine_pk_wine_id[review.wine.pk] + 1] = (
                    review.rating / review.variants
            )

        adjacency_matrix.append(result)
    adjacency_matrix = pd.DataFrame(
        adjacency_matrix, columns=["user_id", *[wine.pk for wine in wines]]
    )
    print("Finish building adjacency matrix")

    return adjacency_matrix


def most_popular_wines(adjacency_matrix: pd.DataFrame) -> List[int]:
    most_popular = np.argsort(
        adjacency_matrix.drop("user_id", axis=1).sum(axis=0)
    ).index
    return most_popular


if os.environ.get("BUILD_MATRIX", False):
    global adjacency_matrix
    adjacency_matrix = build_adjacency_matrix()
    most_popular_index = most_popular_wines(adjacency_matrix)


@swagger_auto_schema(methods=["get", "post"], auto_schema=None)
@api_view(["GET", "POST"])
def user_list(request):
    """
    Получить всех пользователей или добавить нового
    """
    if request.method == "GET":
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = json.loads(request.data)
        if not isinstance(data, list):
            return Response("Data must be array", status=status.HTTP_400_BAD_REQUEST)
        users = []
        for user in data:
            serializer = UserSerializer(data=user)
            if serializer.is_valid():
                serializer.save()
                users.append(serializer.data)
                add_user_in_matrix(serializer.data["id"])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(json.dumps(users), status=status.HTTP_200_OK)


def add_user_in_matrix(id_):
    global adjacency_matrix
    adjacency_matrix.loc[len(adjacency_matrix)] = [int(id_)] + [None] * (
            adjacency_matrix.shape[1] - 1
    )


# TODO: добавить матчинг по названиям
@swagger_auto_schema(methods=["get", "post"], auto_schema=None)
@api_view(["GET", "POST"])
def wine_list(request):
    """
    Получить все вина или добавить новые
    """
    if request.method == "GET":
        wine = Wine.objects.all()
        serializer = WineSerializer(wine, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        data = json.loads(request.data)
        if not isinstance(data, list):
            return Response("Data must be array", status=status.HTTP_400_BAD_REQUEST)
        wines = []
        for wine in data:
            serializer = WineSerializer(data=wine)
            if serializer.is_valid():
                serializer.save()
                wines.append(serializer.data)
                add_wine_in_matrix(serializer.data["id"])
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(json.dumps(wines), status=status.HTTP_200_OK)


def add_wine_in_matrix(id_):
    global adjacency_matrix
    adjacency_matrix[id_] = [None] * adjacency_matrix.shape[0]


@swagger_auto_schema(method="post", auto_schema=None)
@swagger_auto_schema(method="delete", auto_schema=None)
@api_view(["POST", "DELETE"])
def review_list(request):
    """
    Добавить или изменить оценки пользователей по винам
    """
    global adjacency_matrix, most_popular_index
    if request.method == "POST":
        data = json.loads(request.data)
        if not isinstance(data, list):
            return Response("Data must be array", status=status.HTTP_400_BAD_REQUEST)
        for review in data:
            serializer = ReviewSerializer(data=review)
            if serializer.is_valid():
                wine = get_or_create_wine(internal_id=serializer.data["wine"])
                user = get_or_create_user(internal_id=serializer.data["user"])
                review_model = get_or_create_review(wine, user)
                serializer = ReviewModelSerializer(
                    review_model,
                    data={
                        "rating": review["rating"],
                        "variants": review["variants"],
                        "wine": wine.pk,
                        "user": user.pk,
                    },
                )
                if serializer.is_valid():
                    serializer.save()
                    if wine.pk not in adjacency_matrix.columns:
                        add_wine_in_matrix(wine.pk)
                    if user.pk not in adjacency_matrix["user_id"]:
                        add_user_in_matrix(user.pk)
                    index = adjacency_matrix[adjacency_matrix["user_id"] == user.pk].index[
                        0
                    ]
                    adjacency_matrix.loc[index, wine.pk] = float(review["rating"]) / float(
                        review["variants"]
                    )
                    most_popular_index = most_popular_wines(adjacency_matrix)
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"result": "ok"}, status=status.HTTP_200_OK)
    elif request.method == "DELETE":
        data = json.loads(request.data)
        user_id = data["user_id"]
        wine_id = data.get("wine_id", None)
        user = get_or_create_user(internal_id=user_id)
        index = adjacency_matrix[adjacency_matrix["user_id"] == user.pk].index[
            0
        ]
        if wine_id == None:
            reviews = Review.objects.filter(user_id=user.pk)
            for review in reviews:
                adjacency_matrix.loc[index, review.wine_id] = None
                most_popular_index = most_popular_wines(adjacency_matrix)
                review.delete()
        else:
            wine = get_or_create_wine(internal_id=wine_id)
            review_model = get_or_create_review(wine, user)
            adjacency_matrix.loc[index, review_model.wine_id] = None
            most_popular_index = most_popular_wines(adjacency_matrix)
            review_model.delete()
        return Response({"result": "ok"}, status=status.HTTP_200_OK)


def get_or_create_wine(internal_id):
    try:
        wine = Wine.objects.get(internal_id__exact=internal_id)
    except Wine.DoesNotExist:
        wine = Wine.objects.create(internal_id=internal_id)
        add_wine_in_matrix(wine.pk)
    return wine


def get_or_create_user(internal_id):
    try:
        user = User.objects.get(internal_id__exact=internal_id)
    except User.DoesNotExist:
        user = User.objects.create(internal_id=internal_id)
        add_user_in_matrix(user.pk)
    return user


def get_or_create_review(wine, user):
    try:
        review = Review.objects.get(wine=wine, user=user)
    except Review.DoesNotExist:
        review = Review()
    return review


@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "user_id",
            openapi.IN_PATH,
            required=True,
            description="User id, with empty value works too",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            required=False,
            default=0,
            description="Number of page to retrieve. Starts from 0",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "size",
            openapi.IN_QUERY,
            required=False,
            default=10,
            description="Number of elements in one page",
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET"])
def get_recommendations(request, **kwargs):
    return _get_rec(request, **kwargs)

@swagger_auto_schema(
    method="get",
    manual_parameters=[
        openapi.Parameter(
            "page",
            openapi.IN_QUERY,
            required=False,
            default=0,
            description="Number of page to retrieve. Starts from 0",
            type=openapi.TYPE_INTEGER,
        ),
        openapi.Parameter(
            "size",
            openapi.IN_QUERY,
            required=False,
            default=10,
            description="Number of elements in one page",
            type=openapi.TYPE_INTEGER,
        ),
    ],
)
@api_view(["GET"])
def get_recommendations_default(request, **kwargs):
    return _get_rec(request, **kwargs)


def _get_rec(request, **kwargs):
    """
    Получить рекомендацию по конкретному пользователю
    """
    user_id = int(kwargs.get("user_id", 0))
    page = int(request.query_params.get("page", 0))
    size = int(request.query_params.get("size", 10))
    global adjacency_matrix, most_popular_index
    try:
        our_user = User.objects.get(internal_id=user_id)
        wines_ids = model(adjacency_matrix, most_popular_index, our_user.id)
    except User.DoesNotExist:
        wines_ids = most_popular_index
    total = len(wines_ids)
    total_pages = math.ceil(len(wines_ids) / size)
    wines_ids = wines_ids[page * size: (page + 1) * size]
    wines_ids = wine_internal_id_to_wine_external_id(wines_ids)
    result = {
        "content": wines_ids,
        "page": page,
        "size": size,
        "total": total,
        "totalPages": total_pages,
    }
    return Response(result, status=status.HTTP_200_OK)


def wine_internal_id_to_wine_external_id(wines_ids: List[int]) -> List[int]:
    wines = Wine.objects.filter(id__in=wines_ids)
    our_wine_id_to_catalog_wine_id = {wine.pk: wine.internal_id for wine in wines}
    return [our_wine_id_to_catalog_wine_id[our_id] for our_id in wines_ids]


@swagger_auto_schema(method="get", auto_schema=None)
@api_view(["GET"])
def print_matrix(request):
    global adjacency_matrix
    logger.warning(adjacency_matrix)
    return Response(str(adjacency_matrix), status.HTTP_200_OK)


@swagger_auto_schema(method="get", auto_schema=None)
@api_view(["GET"])
def user_sync(request):
    """
    Run job user_sync
    """
    thread = Thread(target=user_sync_job, args=())
    thread.start()
    return Response("{}", status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", auto_schema=None)
@api_view(["GET"])
def catalog_sync(request):
    """
    Run job catalog_sync
    """
    return Response({}, status=status.HTTP_200_OK)
    output = subprocess.Popen(
        ["python", "src/jobs/catalog_sync.py"], stdout=subprocess.PIPE
    )
    return Response([output.stdout, output.stderr], status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", auto_schema=None)
@api_view(["GET"])
def favorites_sync(request):
    """
    Run job favorites_sync
    """
    thread = Thread(target=favorites_sync_job, args=())
    thread.start()
    return Response("{}", status=status.HTTP_200_OK)
