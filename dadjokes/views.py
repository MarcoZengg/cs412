# File: views.py
# Author: Xiankun Zeng (xiankz23@bu.edu), 04/03/2026
# Description: HTML ListView/DetailView pages and DRF API views for dadjokes (A9).
"""Serve browser templates and JSON API endpoints for jokes and pictures."""

from django.views.generic import DetailView, ListView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Joke, Picture
from .serializers import JokeSerializer, PictureSerializer



class RandomJokePictureListView(ListView):
    """Show one random joke and one random picture on the same template."""

    model = Joke
    template_name = "dadjokes/random_pair.html"
    context_object_name = "random_jokes"

    def get_queryset(self):
        """Return a queryset of length one so ListView still drives the page."""
        return Joke.objects.order_by("?")[:1]

    def get_context_data(self, **kwargs):
        """Add single joke and random picture for the template variables."""
        context = super().get_context_data(**kwargs)
        jokes_qs = context["random_jokes"]
        context["joke"] = jokes_qs.first()
        context["picture"] = Picture.objects.order_by("?").first()
        return context


class JokeListView(ListView):
    """Display every joke as a text list with links to detail pages."""

    model = Joke
    template_name = "dadjokes/joke_list.html"
    context_object_name = "jokes"
    ordering = ["-timestamp"]


class JokeDetailView(DetailView):
    """Display the full text and metadata for one joke by pk."""

    model = Joke
    template_name = "dadjokes/joke_detail.html"
    context_object_name = "joke"


class PictureListView(ListView):
    """Display links to each picture detail page (no joke content)."""

    model = Picture
    template_name = "dadjokes/picture_list.html"
    context_object_name = "pictures"
    ordering = ["-timestamp"]


class PictureDetailView(DetailView):
    """Display one picture URL in a fixed-size square frame."""

    model = Picture
    template_name = "dadjokes/picture_detail.html"
    context_object_name = "picture"




class RandomJokeAPIView(APIView):
    """Respond with JSON for one randomly chosen joke."""

    def get(self, request):
        """Pick a random joke or return 404 if the table is empty."""
        joke = Joke.objects.order_by("?").first()
        if joke is None:
            return Response(
                {"detail": "No jokes available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(JokeSerializer(joke).data)


class RandomPictureAPIView(APIView):
    """Respond with JSON for one randomly chosen picture."""

    def get(self, request):
        """Pick a random picture or return 404 if the table is empty."""
        picture = Picture.objects.order_by("?").first()
        if picture is None:
            return Response(
                {"detail": "No pictures available."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(PictureSerializer(picture).data)


class JokeListCreateAPIView(generics.ListCreateAPIView):
    """List all jokes on GET; create a joke from JSON body on POST."""

    queryset = Joke.objects.all().order_by("-timestamp")
    serializer_class = JokeSerializer
    # Disable global PageNumberPagination so the client receives the full list.
    pagination_class = None


class JokeRetrieveAPIView(generics.RetrieveAPIView):
    """Return JSON for exactly one joke identified by pk in the URL."""

    queryset = Joke.objects.all()
    serializer_class = JokeSerializer


class PictureListAPIView(generics.ListAPIView):
    """Return JSON list of all pictures."""

    queryset = Picture.objects.all().order_by("-timestamp")
    serializer_class = PictureSerializer
    pagination_class = None


class PictureRetrieveAPIView(generics.RetrieveAPIView):
    """Return JSON for one picture identified by pk in the URL."""

    queryset = Picture.objects.all()
    serializer_class = PictureSerializer
