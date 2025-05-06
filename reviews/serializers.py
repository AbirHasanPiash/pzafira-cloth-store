from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'user_id', 'rating', 'comment', 'created_at', 'updated_at']
        read_only_fields = ['user', 'user_id', 'created_at', 'updated_at']
