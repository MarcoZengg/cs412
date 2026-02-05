from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Page URLs: home, order form, confirmation (after submit)
urlpatterns = [
    path(r'', views.main, name="main"),
    path(r'order', views.order, name="order"),
    path(r'confirmation', views.confirmation, name="confirmation"),
]
# CSS file for styling
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)