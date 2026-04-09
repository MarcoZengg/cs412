"""DRF serializers for mini_insta Assignment 10 Task 1 API endpoints."""

from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Photo, Post, Profile


class ProfileSerializer(serializers.ModelSerializer):
    """Serialize basic profile data for list/detail endpoints."""

    class Meta:
        model = Profile
        fields = [
            "id",
            "username",
            "display_name",
            "profile_image_url",
            "bio_text",
            "join_date",
        ]


class PhotoSerializer(serializers.ModelSerializer):
    """Serialize photo data with a resolved URL field."""

    # The Photo model may store either `image_url` or uploaded `image_file`.
    # Expose one normalized `image` field to keep API consumers simple.
    image = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ["id", "image", "timestamp"]

    def get_image(self, obj):
        """Return whichever image source is available for the photo."""
        return obj.get_image_url()


class PostSerializer(serializers.ModelSerializer):
    """Serialize posts with attached photos and author profile id."""

    # Nest photos directly in the post payload so clients can render posts in one request.
    photos = PhotoSerializer(source="photo_set", many=True, read_only=True)
    # Expose the profile's PK explicitly to avoid nested profile payloads on feed/list endpoints.
    profile_id = serializers.IntegerField(source="profile.id", read_only=True)

    class Meta:
        model = Post
        fields = ["id", "profile_id", "caption", "timestamp", "photos"]


class CreatePostSerializer(serializers.ModelSerializer):
    """Validate and create posts via API requests."""

    # API clients submit `profile_id`; map it to the Post.profile FK for model save.
    profile_id = serializers.PrimaryKeyRelatedField(
        source="profile",
        queryset=Profile.objects.all(),
        write_only=True,
    )

    class Meta:
        model = Post
        fields = ["id", "profile_id", "caption", "timestamp"]
        read_only_fields = ["id", "timestamp"]

class UserSerializer(serializers.ModelSerializer):
    # Never return password values in API responses.
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        # Use Django's create_user so password hashing and auth defaults are correct.
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email')
        )
        return user