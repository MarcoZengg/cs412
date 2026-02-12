from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import ProfileListView


from django.urls import path

urlpatterns = [
    path('', ProfileListView.as_view(), name="show_all_profiles"),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
