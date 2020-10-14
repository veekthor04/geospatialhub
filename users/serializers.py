from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:

        model = Profile
        fields = ('id', 'first_name', 'last_name','phone','bio','date_of_birth', 'location_city', 'location_state','location_country','company' , )

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:

        model = get_user_model()
        fields = ('id', 'username','email', 'profile' )

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        
        profile = instance.profile

        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.first_name = profile_data.get('first_name', profile.first_name)
        profile.last_name = profile_data.get('last_name', profile.last_name)
        profile.phone = profile_data.get('phone', profile.phone)
        profile.bio = profile_data.get('bio', profile.bio)
        profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
        profile.location_city = profile_data.get('location_city', profile.location_city)
        profile.location_state = profile_data.get('location_state', profile.location_state)
        profile.location_country = profile_data.get('location_country', profile.location_country)
        profile.company = profile_data.get('company', profile.company)

        profile.save()

        return instance
