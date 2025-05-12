from django.urls import path
from .views import CommitsView

urlpatterns = [
    path('commits/', CommitsView.as_view(), name='commits'),
]
