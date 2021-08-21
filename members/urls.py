from django.urls import path

from .views import PersonDetailView, PersonListView

app_name = 'members'

urlpatterns = [
    path('', PersonListView.as_view(), name='list'),
    path('<int:pk>/', PersonDetailView.as_view(), name='detail'),
]
