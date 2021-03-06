from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_auth.serializers import TokenSerializer
from .models import Profile, Post, PostRate, Follower, Message, Notification


class ProfileUserSerializer(serializers.ModelSerializer):

    class Meta:

        model = get_user_model()
        fields = ('username','email')

class ProfileSerializer(serializers.ModelSerializer):
    follow_status = serializers.CharField(source='get_follow_status')
    enrolled_for = serializers.ListField(source='get_enrolled_for')
    unread_count = serializers.IntegerField(source='get_unread_count')
    post_count = serializers.IntegerField(source='get_post_count')
    user = ProfileUserSerializer()

    class Meta:

        model = Profile
        fields = ('id', 'user', 'first_name', 'last_name','phone', 'profile_pic', 'banner_pic','bio','date_of_birth', 'location_city', 'location_state','location_country','organisation', 'institution', 'occupation' ,'follower_count', 'following_count', 'follow_status', 'unread_count', 'post_count', 'enrolled_for' )
        read_only_fields = ('follower_count', 'following_count', 'follow_status', 'unread_count', 'enrolled_for', 'post_count')

class ListProfileSerializer(serializers.ModelSerializer):
    follow_status = serializers.CharField(source='get_follow_status')

    class Meta:

        model = Profile
        fields = ('first_name', 'last_name', 'profile_pic', 'follower_count', 'following_count', 'follow_status')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:

        model = get_user_model()
        fields = ('id', 'username','email', 'profile' )
        # read_only_fields = ('profile__follower_count', 'profile__following_count', 'profile__follow_status', 'profile__unread_count', 'profile__enrolled_for', 'profile__post_count')
        

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
        profile.organisation = profile_data.get('organisation', profile.company)
        profile.occupation = profile_data.get('occupation', profile.company)
        profile.institution = profile_data.get('institution', profile.company)

        profile.save()

        return instance


class ListUserSerializer(serializers.ModelSerializer):
    profile = ListProfileSerializer()

    class Meta:

        model = get_user_model()
        fields = ('id', 'username', 'profile' )


class CustomTokenSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)

    class Meta(TokenSerializer.Meta):
        fields = ('key', 'user') 


class PostSerializer(serializers.ModelSerializer):
    post_belongs_to_authenticated_user = serializers.BooleanField(source = 'get_post_belongs_to_authenticated_user', read_only = True)
    authenticated_user_like_status = serializers.BooleanField(source = 'get_authenticated_user_like_status', read_only = True)
    posted_by = serializers.DictField(child = serializers.CharField(), source = 'get_user', read_only = True)
    likes_count = serializers.IntegerField(source='get_likes_count', read_only = True)
    comments_count = serializers.IntegerField(source='get_comments_count', read_only = True)

    class Meta:
        model = Post
        fields = ['id', 'post_belongs_to_authenticated_user', 'authenticated_user_like_status' ,'posted_by', 'pub_date', 'text', 'image', 'in_reply_to_post', 'likes_count', 'comments_count']
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
        fields = ('user', 'is_followed_by', 'created')
        read_only_fields = ('user', 'is_followed_by')

class MyFollowerSerializer(serializers.ModelSerializer):
    user = serializers.DictField(child = serializers.CharField(), source = 'get_user_info', read_only = True)
    is_followed_by = serializers.DictField(child = serializers.CharField(), source = 'get_is_followed_by_info', read_only = True)

    class Meta:
        model = Follower
        fields = ('user', 'is_followed_by', 'created', 'is_viewed')
        read_only_fields = ('user', 'is_followed_by')

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.DictField(child = serializers.CharField(), source = 'get_sender', read_only = True)
    receiver = serializers.DictField(child = serializers.CharField(), source = 'get_receiver', read_only = True)


    class Meta:
        model = Message
        fields = ['sender', 'text', 'receiver', 'created', 'is_read']
        write_only_fields = ['text', 'receiver']


class NotificationSerializer(serializers.ModelSerializer):

    course = serializers.DictField(child = serializers.CharField(),source='get_course')
    follower = serializers.DictField(child=serializers.CharField(), source='get_follower')

    class Meta:
        model = Notification
        fields = ('id', 'event', 'follower','course', 'created', 'is_read')