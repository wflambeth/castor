from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:sched_id>', views.schedule, name='schedule'),
    path('create', views.create, name='create'),
    path('save', views.save, name='save'),
    path('delete', views.delete, name='delete'),
    path('update_title', views.update_title, name='update_title')
]
