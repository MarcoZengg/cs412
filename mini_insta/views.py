# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 2/12/2026
# Description: Class-based views for mini_insta: list/detail for profiles and
#              posts, create/update/delete post, update profile, followers/
#              following, feed, and search. Create/Update/Delete and feed/search
#              require login via MiniInstaLoginRequiredMixin.

from .models import Profile, Post, Photo, Follow, Like, Comment
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect
from .forms import CreatePostForm, CreateProfileForm, CreateCommentForm, UpdateProfileForm, UpdatePostForm
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import (
    CreatePostSerializer,
    PostSerializer,
    ProfileSerializer,
    UserSerializer,
)


# -----------------------------------------------------------------------------
# Mixin: require login and provide helpers for the logged-in user's Profile.
# -----------------------------------------------------------------------------
class HeaderFallbackTokenAuthentication(TokenAuthentication):
    """Read token from X-Auth-Token first, then fall back to Authorization."""

    def authenticate(self, request):
        x_auth_token = request.META.get("HTTP_X_AUTH_TOKEN")
        if x_auth_token:
            return self.authenticate_credentials(x_auth_token)
        return super().authenticate(request)


class MiniInstaLoginRequiredMixin(LoginRequiredMixin):
    """Require authentication; redirect to login with ?next= for post-login redirect."""

    def get_login_url(self):
        """Redirect to mini_insta login; next is set by LoginRequiredMixin for post-login redirect."""
        return reverse('mini_insta_login')

    def get_logged_in_user_profile(self):
        """Return the Profile linked to the logged-in user, or None if none exists."""
        return Profile.objects.filter(user=self.request.user).first()

    def get_logged_in_user_profile_or_404(self):
        """Return the Profile for the logged-in user; raise Http404 if none (e.g. admin with multiple)."""
        profile = self.get_logged_in_user_profile()
        if profile is None:
            raise Http404("No profile found for this user.")
        return profile


# -----------------------------------------------------------------------------
# List view: display all profiles (no login required).
# -----------------------------------------------------------------------------
class ProfileListView(ListView):
    """Return a page listing all Profile records."""

    model = Profile
    template_name = 'mini_insta/show_all_profiles.html'
    context_object_name = 'profiles'


# -----------------------------------------------------------------------------
# Create profile view: UserCreationForm + CreateProfileForm in one form; no login required.
# -----------------------------------------------------------------------------
class CreateProfileView(CreateView):
    """Show UserCreationForm and CreateProfileForm together; on submit create User, log in, create Profile."""

    model = Profile
    form_class = CreateProfileForm
    template_name = 'mini_insta/create_profile_form.html'

    def get_context_data(self, **kwargs):
        """Add UserCreationForm to context so the template can render both forms."""
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()
        return context

    def form_valid(self, form):
        """Create User from UserCreationForm, log them in, attach user to Profile, then save Profile."""
        user_form = UserCreationForm(self.request.POST)
        # If account fields are invalid, re-render with errors and do not create User/Profile:
        if not user_form.is_valid():
            context = self.get_context_data(form=form)
            context['user_form'] = user_form
            return self.render_to_response(context)
        user = user_form.save()
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        form.instance.user = user
        form.instance.username = user.username
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the new user's profile page after creation."""
        return reverse('show_my_profile')


# -----------------------------------------------------------------------------
# Detail view: display one profile by primary key from URL (any profile).
# -----------------------------------------------------------------------------
class ProfileDetailView(DetailView):
    """Return a page for one Profile; pk comes from URL (profile/<pk>/)."""

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        """Add is_following and my_profile so template can show Follow/Unfollow (and hide for own profile)."""
        context = super().get_context_data(**kwargs)
        profile = self.object
        my_profile = Profile.objects.filter(user=self.request.user).first() if self.request.user.is_authenticated else None
        context['my_profile'] = my_profile
        # Only check is_following when viewing another user's profile (not own):
        if my_profile and my_profile != profile:
            context['is_following'] = Follow.objects.filter(profile=profile, follower_profile=my_profile).exists()
        else:
            context['is_following'] = False
        return context


# -----------------------------------------------------------------------------
# Follow / Unfollow views (login required; POST only; redirect back to profile).
# -----------------------------------------------------------------------------
class FollowProfileView(MiniInstaLoginRequiredMixin, View):
    """Create a Follow from the logged-in user's profile to the profile identified by pk."""

    def post(self, request, *args, **kwargs):
        my_profile = self.get_logged_in_user_profile_or_404()
        target = Profile.objects.get(pk=kwargs['pk'])
        # Only create Follow if the user is not trying to follow themselves:
        if my_profile != target:
            Follow.objects.get_or_create(profile=target, follower_profile=my_profile)
        return redirect('show_profile', pk=target.pk)


class DeleteFollowView(MiniInstaLoginRequiredMixin, View):
    """Remove the Follow from the logged-in user's profile to the profile identified by pk."""

    def post(self, request, *args, **kwargs):
        my_profile = self.get_logged_in_user_profile_or_404()
        target = Profile.objects.get(pk=kwargs['pk'])
        Follow.objects.filter(profile=target, follower_profile=my_profile).delete()
        return redirect('show_profile', pk=target.pk)


# -----------------------------------------------------------------------------
# Detail view: display the logged-in user's own profile (no pk in URL).
# -----------------------------------------------------------------------------
class MyProfileDetailView(MiniInstaLoginRequiredMixin, DetailView):
    """Show the logged-in user's Profile; object from get_object, not URL pk."""

    model = Profile
    template_name = 'mini_insta/show_profile.html'
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the Profile for the logged-in user; 404 if none or ambiguous (e.g. admin)."""
        return self.get_logged_in_user_profile_or_404()


# -----------------------------------------------------------------------------
# Detail view: display one post by primary key from URL.
# -----------------------------------------------------------------------------
class PostDetailView(DetailView):
    """Return a page for one Post; pk comes from URL (post/<pk>/)."""

    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Add profile, my_profile, and has_liked so template can show Like/Unlike (and hide for own post)."""
        context = super().get_context_data(**kwargs)
        post = self.object
        context['profile'] = post.profile
        context['comment_form'] = CreateCommentForm()
        my_profile = Profile.objects.filter(user=self.request.user).first() if self.request.user.is_authenticated else None
        context['my_profile'] = my_profile
        # Only check has_liked when viewing another user's post (not own):
        if my_profile and post.profile != my_profile:
            context['has_liked'] = Like.objects.filter(post=post, profile=my_profile).exists()
        else:
            context['has_liked'] = False
        return context


# -----------------------------------------------------------------------------
# Like / Unlike views (login required; POST only; redirect back to post).
# -----------------------------------------------------------------------------
class LikePostView(MiniInstaLoginRequiredMixin, View):
    """Create a Like from the logged-in user's profile for the post identified by pk."""

    def post(self, request, *args, **kwargs):
        my_profile = self.get_logged_in_user_profile_or_404()
        post = Post.objects.get(pk=kwargs['pk'])
        # Do not allow a user to like their own post:
        if post.profile != my_profile:
            Like.objects.get_or_create(post=post, profile=my_profile)
        return redirect('show_post', pk=post.pk)


class DeleteLikeView(MiniInstaLoginRequiredMixin, View):
    """Remove the Like from the logged-in user's profile for the post identified by pk."""

    def post(self, request, *args, **kwargs):
        my_profile = self.get_logged_in_user_profile_or_404()
        post = Post.objects.get(pk=kwargs['pk'])
        Like.objects.filter(post=post, profile=my_profile).delete()
        return redirect('show_post', pk=post.pk)


# -----------------------------------------------------------------------------
# Create comment view (login required); redirects to post after adding comment.
# -----------------------------------------------------------------------------
class CreateCommentView(MiniInstaLoginRequiredMixin, CreateView):
    """Add a Comment to the Post identified by pk; redirect to that post after success."""

    model = Comment
    form_class = CreateCommentForm
    template_name = 'mini_insta/show_post.html'

    def get(self, request, *args, **kwargs):
        """GET create_comment URL just redirects to the post page."""
        return redirect('show_post', pk=kwargs['pk'])

    def get_context_data(self, **kwargs):
        """Build same context as PostDetailView so show_post template renders correctly."""
        context = super().get_context_data(**kwargs)
        post = Post.objects.get(pk=self.kwargs['pk'])
        context['post'] = post
        context['profile'] = post.profile
        context['comment_form'] = context.get('form', CreateCommentForm())
        my_profile = self.get_logged_in_user_profile()
        context['my_profile'] = my_profile
        # Only check has_liked when the viewer is not the post owner:
        if my_profile and post.profile != my_profile:
            context['has_liked'] = Like.objects.filter(post=post, profile=my_profile).exists()
        else:
            context['has_liked'] = False
        return context

    def form_valid(self, form):
        """Set post and profile on the comment, then save."""
        form.instance.post = Post.objects.get(pk=self.kwargs['pk'])
        form.instance.profile = self.get_logged_in_user_profile_or_404()
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the post on which the user commented."""
        return reverse('show_post', kwargs={'pk': self.kwargs['pk']})


# -----------------------------------------------------------------------------
# Create view: display and process the "create post" form (login required).
# -----------------------------------------------------------------------------
class CreatePostView(MiniInstaLoginRequiredMixin, CreateView):
    """Display create-post form and, on valid submit, save Post and optional Photo."""

    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        """Add the logged-in user's Profile to context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
        return context

    def form_valid(self, form):
        """Attach the logged-in user's Profile to the Post, then save and add photos."""
        profile = self.get_logged_in_user_profile_or_404()
        form.instance.profile = profile

        response = super().form_valid(form)
        # The newly saved Post instance, needed to attach Photo records:
        post = form.instance

        # Previously: create Photo from image URL (commented out).
        # photo_url = self.request.POST.get('photo_url', '').strip()
        # if photo_url:
        #     Photo.objects.create(post=post, image_url=photo_url)

        # Create one Photo per uploaded file (from input name="files" with multiple).
        files = self.request.FILES.getlist('files')
        for f in files:
            # Each uploaded file becomes a separate Photo linked to this post:
            Photo.objects.create(post=post, image_file=f)

        return response

    def get_success_url(self):
        """Redirect to the new Post's detail page after successful creation."""
        return reverse('show_post', kwargs={'pk': self.object.pk})


class UpdateProfileView(MiniInstaLoginRequiredMixin, UpdateView):
    """Update the logged-in user's Profile; object from get_object, not URL pk."""

    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"
    context_object_name = 'profile'

    def get_object(self, queryset=None):
        """Return the Profile for the logged-in user; 404 if none or ambiguous."""
        return self.get_logged_in_user_profile_or_404()

    def get_success_url(self):
        """Redirect to the logged-in user's profile page after update."""
        return reverse('show_my_profile')


class DeletePostView(MiniInstaLoginRequiredMixin, DeleteView):
    """Delete a Post; redirect to the post's profile page after delete."""

    model = Post
    template_name = "mini_insta/delete_post_form.html"
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        """Provide post (Post to delete) and profile (owner) for the template."""
        context = super().get_context_data(**kwargs)
        # Add the post's owner so template can link back to profile after cancel:
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        """Redirect to the logged-in user's profile page after delete."""
        return reverse('show_my_profile')


class UpdatePostView(MiniInstaLoginRequiredMixin, UpdateView):
    """Update a Post (caption); redirect to that post's detail page after save."""

    model = Post
    form_class = UpdatePostForm
    template_name = "mini_insta/update_post_form.html"
    context_object_name = 'post'

    def get_success_url(self):
        """Redirect to the show_post page for this post."""
        return reverse('show_post', kwargs={'pk': self.object.pk})

# -----------------------------------------------------------------------------
# Detail views: show followers list and following list for a profile (by pk).
# -----------------------------------------------------------------------------
class ShowFollowersDetailView(DetailView):
    """DetailView for a Profile; template shows this profile's followers."""

    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = 'profile'


class ShowFollowingDetailView(DetailView):
    """DetailView for a Profile; template shows who this profile follows."""

    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = 'profile'

# -----------------------------------------------------------------------------
# List view: post feed for the logged-in user (posts from followed profiles).
# -----------------------------------------------------------------------------
class PostFeedListView(MiniInstaLoginRequiredMixin, ListView):
    """List view of the post feed for the logged-in user's profile."""

    template_name = "mini_insta/show_feed.html"
    context_object_name = 'posts'

    def get_queryset(self):
        """Return the feed of Posts for the logged-in user's profile."""
        profile = self.get_logged_in_user_profile_or_404()
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        """Add the logged-in user's profile to context."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
        return context

# -----------------------------------------------------------------------------
# Search view: form (search.html) or results (search_results.html) by GET param q.
# -----------------------------------------------------------------------------
class SearchView(MiniInstaLoginRequiredMixin, ListView):
    """Search Profiles and Posts by text; form on search.html, results on search_results.html."""

    template_name = "mini_insta/search_results.html"
    context_object_name = 'posts'

    def dispatch(self, request, *args, **kwargs):
        """If query is absent from GET, show search form; otherwise run ListView."""
        # No query in GET: show the search form page instead of results:
        if 'q' not in request.GET:
            profile = Profile.objects.filter(user=request.user).first()
            if profile is None:
                raise Http404("No profile found for this user.")
            return render(request, 'mini_insta/search.html', {'profile': profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Return Posts whose caption contains the query string."""
        query = self.request.GET.get('q', '').strip()
        return Post.objects.filter(caption__icontains=query).order_by('-timestamp')

    def get_context_data(self, **kwargs):
        """Add profile, query, and matching profiles to context; posts from get_queryset."""
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_logged_in_user_profile_or_404()
        # Search term for display and for filtering profiles:
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        # Profiles matching query in username, display_name, or bio_text:
        context['profiles'] = Profile.objects.filter(
            Q(username__icontains=query) |
            Q(display_name__icontains=query) |
            Q(bio_text__icontains=query)
        )
        return context


# -----------------------------------------------------------------------------
# REST API views (Assignment 10). Task 3: Token auth + permissions on views.
# -----------------------------------------------------------------------------
class APIProfileListView(generics.ListAPIView):
    """Return JSON for all profiles. GET is public; unsafe methods disallowed by DRF."""

    authentication_classes = [HeaderFallbackTokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Profile.objects.all().order_by("id")
    serializer_class = ProfileSerializer
    pagination_class = None


class APIProfileDetailView(generics.RetrieveAPIView):
    """Return JSON for a single profile by id."""

    authentication_classes = [HeaderFallbackTokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer


class APIProfilePostsView(generics.ListAPIView):
    """Return JSON posts (including pictures) for one profile."""

    authentication_classes = [HeaderFallbackTokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = None

    def get_queryset(self):
        return Post.objects.filter(profile__pk=self.kwargs["pk"]).order_by("-timestamp")


class APIProfileFeedView(generics.ListAPIView):
    """Return JSON feed posts for one profile id."""

    authentication_classes = [HeaderFallbackTokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = PostSerializer
    pagination_class = None

    def get_queryset(self):
        profile = Profile.objects.filter(pk=self.kwargs["pk"]).first()
        if profile is None:
            return Post.objects.none()
        return profile.get_post_feed()


class APICreatePostView(APIView):
    """Create a new post; requires token. Post must belong to the authenticated user's Profile."""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # return Response({"auth": request.META.get("HTTP_AUTHORIZATION")})
        user_profile = Profile.objects.filter(user=request.user).first()
        if user_profile is None:
            return Response(
                {"detail": "No MiniInsta profile is linked to this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        target_profile = serializer.validated_data["profile"]
        if target_profile.pk != user_profile.pk:
            return Response(
                {"detail": "You may only create posts for your own profile."},
                status=status.HTTP_403_FORBIDDEN,
            )

        post = serializer.save()

        # Support either one image_url string or image_urls list in the payload.
        image_url = request.data.get("image_url", "").strip()
        if image_url:
            Photo.objects.create(post=post, image_url=image_url)

        image_urls = request.data.get("image_urls", [])
        if isinstance(image_urls, list):
            for url in image_urls:
                clean_url = str(url).strip()
                if clean_url:
                    Photo.objects.create(post=post, image_url=clean_url)

        return Response(PostSerializer(post).data, status=status.HTTP_201_CREATED)


class UserRegistrationView(generics.CreateAPIView):
    """Sign-up: create User (password hashed). No token required."""

    authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


class UserLoginView(APIView):
    """Sign-in: return DRF auth token and linked Profile id for the mobile client."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"detail": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            request=request,
            username=username,
            password=password,
        )
        if user is None:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token, _created = Token.objects.get_or_create(user=user)
        profile = Profile.objects.filter(user=user).first()
        return Response(
            {
                "token": token.key,
                "profile_id": profile.pk if profile else None,
            },
            status=status.HTTP_200_OK,
        )

class APIDebugAuthView(APIView):
    """Temporary debug endpoint — shows what headers Apache passes to Django."""
    authentication_classes = []
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            "HTTP_AUTHORIZATION": request.META.get("HTTP_AUTHORIZATION"),
            "HTTP_X_AUTH_TOKEN": request.META.get("HTTP_X_AUTH_TOKEN"),
        })
    def post(self, request):
        return self.get(request)
