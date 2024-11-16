from rest_framework import serializers
from .models import Result

class AgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'