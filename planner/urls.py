from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedule/<int:sched_id>', views.router, name='router'),
    path('create', views.create, name='create'),
    path('save', views.save, name='save'),
    path('update_title', views.update_title, name='update_title')
]
