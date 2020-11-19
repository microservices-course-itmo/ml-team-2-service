from rest_framework import serializers
from .models import Wine, User, Review


class WineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wine
        fields = ["id", "internal_id", "all_names"]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "internal_id"]


class ReviewSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    rating = serializers.IntegerField(required=True)
    variants = serializers.IntegerField(required=True)
    wine = serializers.IntegerField(required=True)
    user = serializers.IntegerField(required=True)


class ReviewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "rating", "variants", "wine", "user"]
