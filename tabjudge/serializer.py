from rest_framework import serializers

from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('sender', 'title', 'body', 'created_at', 'updated_at', 'lat', 'lng', 'status')