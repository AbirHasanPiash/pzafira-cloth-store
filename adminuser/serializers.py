from rest_framework import serializers
from products.models import Product
from users.models import User

class TopProductSerializer(serializers.ModelSerializer):
    total_reviews = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'average_rating', 'total_reviews']


class TopUserSerializer(serializers.ModelSerializer):
    total_purchased = serializers.IntegerField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'total_purchased']
