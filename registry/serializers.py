from rest_framework import serializers


class CreateUserSerializer(serializers.Serializer):
    firstNames = serializers.CharField()
    middleNames = serializers.CharField(required=False, allow_blank=True)
    lastNames = serializers.CharField()

    birthDate = serializers.DateField()
    email = serializers.EmailField()

    memberCategory = serializers.ChoiceField(choices=['alum', 'friend', 'faculty'])
    memberTier = serializers.ChoiceField(choices=['starter', 'regular', 'patron'])

    tos = serializers.BooleanField(required=True)


    def create(self, validated_data):
        return validated_data
