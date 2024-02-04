from rest_framework import serializers

class ValidationResultSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    has_warning = serializers.BooleanField()
    info = serializers.CharField(max_length=2048)

