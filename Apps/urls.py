from django.urls import path
from .views import Index, Country

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('country/', Country.as_view(), name='country'),  # Assurez-vous que l'URL est correcte
    # Autres URLs...
]
