from rest_framework import serializers
from .models import Functionality

class FunctionalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Functionality
        fields = '__all__'