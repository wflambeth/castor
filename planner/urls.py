from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schedules', views.create, name='create'),
    path('schedules/<int:sched_id>', views.sched_router, name='sched_router'),
]
