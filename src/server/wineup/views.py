import os
import subprocess
from typing import List
import json
import logging

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


def build_adjacency_matrix() -> pd.DataFrame:
    print("Start building adjacency matrix")
    users = User.objects.all()
    wines = Wine.objects.order_by("pk").all()
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
    most_popular = np.argsort(adjacency_matrix.sum(axis=0))
    most_popular_index = adjacency_matrix.index[most_popular][::-1]
    return most_popular_index


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
                global adjacency_matrix
                adjacency_matrix.loc[len(adjacency_matrix)] = [
                    int(serializer.data["id"])
                ] + [None] * (adjacency_matrix.shape[1] - 1)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(json.dumps(users), status=status.HTTP_200_OK)


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
                global adjacency_matrix
                adjacency_matrix[serializer.data["id"]] = [
                    None
                ] * adjacency_matrix.shape[0]
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(json.dumps(wines), status=status.HTTP_200_OK)


@swagger_auto_schema(method="post", auto_schema=None)
@api_view(["POST"])
def review_list(request):
    """
    Добавить или изменить оценку пользователя по конкретному вину
    """
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid():
        try:
            wine = Wine.objects.get(internal_id__exact=serializer.data["wine"])
            user = User.objects.get(internal_id__exact=serializer.data["user"])
        except Wine.DoesNotExist:
            return Response(
                f"Wine with id {serializer.data['wine']} does not exist",
                status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                f"User with id {serializer.data['user']} does not exist",
                status.HTTP_400_BAD_REQUEST,
            )
        try:
            review = Review.objects.get(wine=wine, user=user)
        except Review.DoesNotExist:
            review = Review()
        serializer = ReviewModelSerializer(
            review,
            data={
                "rating": request.data["rating"],
                "variants": request.data["variants"],
                "wine": wine.pk,
                "user": user.pk,
            },
        )
        if serializer.is_valid():
            serializer.save()
            global adjacency_matrix, most_popular_index
            index = adjacency_matrix[adjacency_matrix["user_id"] == user.pk].index[0]
            adjacency_matrix.loc[index, wine.pk] = float(
                request.data["rating"]
            ) / float(request.data["variants"])
            most_popular_index = most_popular_wines(adjacency_matrix)
            return Response({"result": "ok"}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_recommendations(request, user_id):
    """
    Получить рекомендацию по конкретному пользователю
    """
    global adjacency_matrix
    # TODO: Вместо ошибки возвращать самые популярные вина
    try:
        our_user = User.objects.get(internal_id=user_id)
    except Wine.DoesNotExist:
        return Response(
            f"User with id {user_id} does not exist",
            status.HTTP_400_BAD_REQUEST,
        )
    wines_id = model(adjacency_matrix, most_popular_index, our_user.id)
    offset = int(request.query_params.get("offset", 0))
    amount = int(request.query_params.get("amount", 20))
    print(offset, amount)
    return Response({"wine_id": wines_id[offset:amount]}, status=status.HTTP_200_OK)


@swagger_auto_schema(method="get", auto_schema=None)
@api_view(["GET"])
def print_matrix(request):
    global adjacency_matrix
    logging.info(adjacency_matrix)
    return Response({}, status.HTTP_200_OK)


@api_view(["GET"])
def user_sync(request):
    """
    Run job user_sync
    """
    output = subprocess.Popen(
        ["python", "src/jobs/user_sync.py"], stdout=subprocess.PIPE
    )
    return Response([output.stdout, output.stderr], status=status.HTTP_200_OK)


@api_view(["GET"])
def catalog_sync(request):
    """
    Run job catalog_sync
    """
    output = subprocess.Popen(
        ["python", "src/jobs/catalog_sync.py"], stdout=subprocess.PIPE
    )
    return Response([output.stdout, output.stderr], status=status.HTTP_200_OK)

@api_view(["GET"])
def favorites_sync(request):
    """
    Run job favorites_sync
    """
    output = subprocess.Popen(
        ["python", "src/jobs/favorites_sync.py"], stdout=subprocess.PIPE
    )
    return Response([output.stdout, output.stderr], status=status.HTTP_200_OK)
