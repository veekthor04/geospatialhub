from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_auth.serializers import TokenSerializer
from .models import Profile, Post, PostRate, Follower


class ProfileSerializer(serializers.ModelSerializer):
    followers_count = serializers.IntegerField(source = 'get_followers_count')
    following_count = serializers.IntegerField(source = 'get_following_count')
    follow_status = serializers.CharField(source = 'get_follow_status')
    enrolled_for = serializers.ListField(source='get_enrolled_for')

    class Meta:

        model = Profile
        fields = ('id', 'first_name', 'last_name','phone', 'profile_pic','bio','date_of_birth', 'location_city', 'location_state','location_country','company' , 'followers_count', 'following_count', 'follow_status', 'enrolled_for' )

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

class CustomTokenSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user') 


class PostSerializer(serializers.ModelSerializer):
    post_belongs_to_authenticated_user = serializers.BooleanField(source = 'get_post_belongs_to_authenticated_user', read_only = True)
    posted_by = serializers.DictField(child = serializers.CharField(), source = 'get_user', read_only = True)
    likes_count = serializers.IntegerField(source='get_likes_count', read_only = True)
    comments_count = serializers.IntegerField(source='get_comments_count', read_only = True)

    class Meta:
        model = Post
        fields = ['id', 'post_belongs_to_authenticated_user', 'posted_by', 'pub_date', 'text', 'image', 'in_reply_to_post', 'likes_count', 'comments_count']
        write_only_fields = ['text', 'image', 'in_reply_to_post']
        
class PostRateSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostRate
        fields = ['liked', 'rated_post']


class FollowerSerializer(serializers.ModelSerializer):
    user = serializers.DictField(child = serializers.CharField(), source = 'get_user_info', read_only = True)
    is_followed_by = serializers.DictField(child = serializers.CharField(), source = 'get_is_followed_by_info', read_only = True)

    class Meta:
        model = Follower
        fields = ('user', 'is_followed_by')
        read_only_fields = ('user', 'is_followed_by')