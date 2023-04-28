from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule', views.create, name='create'),
    path('schedule/<int:sched_id>', views.router, name='router'),
]
