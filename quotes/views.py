from django.shortcuts import render

# Create your views here.
from django.http import HttpRequest, HttpResponse
import random

image_urls = [
            'https://res.cloudinary.com/aenetworks/image/upload/c_fill,ar_2,w_3840,h_1920,g_auto/dpr_auto/f_auto/q_auto:eco/v1/donald-trump-gettyimages-687193180?_a=BAVAZGID0',
            'https://media.cnn.com/api/v1/images/stellar/prod/ap25079762478310.jpg?c=16x9&q=h_833,w_1480,c_fill',
            'https://www.radiofrance.fr/pikapi/images/59d1a59b-6572-4382-8090-6554506d1400/1200x680?webp=false',
            'https://npr.brightspotcdn.com/dims3/default/strip/false/crop/4865x3244+0+0/resize/1100/quality/50/format/jpeg/?url=http%3A%2F%2Fnpr-brightspot.s3.amazonaws.com%2F8b%2F6a%2F3e49c0da453c8467d1ee5097cb7c%2Fgettyimages-2208195300-2.jpg',
        ]

quotes = [
            "Make America Great Again!",
            "There will be tariff comming soon!",
            "I will be in white house for the 3rd term of US president! You are welcome."
            ]

def quote(request):
    template = 'quote.html'
    context = {
        "quote_images" : random.choice(image_urls),
        "quote" : random.choice(quotes)
    }

    return render(request, template, context)

def show_all(request):
    template = 'show_all.html'
    context = {
        "quote_images" : image_urls,
        "quote" : quotes
    }
    return render(request, template, context)

# def show_all(request):
#     template = 'show_all.html'
#     # Pair images with quotes, using None for quotes if there are more images
#     quote_pairs = list(zip(image_urls, quotes + [None] * (len(image_urls) - len(quotes))))
#     context = {
#         "quote_pairs": quote_pairs,
#     }
#     return render(request, template, context)

def about(request):
    template = 'about.html'
    context = {
        "quote_images" : random.choice(image_urls),
    }

    return render(request, template, context)