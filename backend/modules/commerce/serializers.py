from rest_framework import serializers


class CartLineWriteSerializer(serializers.Serializer):
    listing_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1)


class CartQuantitySerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
