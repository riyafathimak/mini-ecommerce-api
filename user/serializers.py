from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile
from rest_framework import serializers
from .models import User
from rest_framework import generics



class UserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='get_full_name', read_only=True)
    image = serializers.ImageField(source='profile.image', required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'name', 'email', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # Create empty profile for image
        Profile.objects.create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
   