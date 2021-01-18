from rest_framework import serializers

from runa.core.models import Category


class CategorySerializer(serializers.Serializer):
    id = serializers.IntegerField(**{
        'min_value': 1
    }, default=None)
    name = serializers.CharField(max_length=32)
    parents = serializers.ListField(required=False)
    children = serializers.ListField(required=False)
    siblings = serializers.ListField(required=False)

    def create(self, validated_data):
        return Category.objects.create(**validated_data)
