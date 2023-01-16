from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', include('planner.urls')),
    path("sG8muBDox7No4g/", admin.site.urls),
    path("accounts/", include('allauth.urls')),
    path("accounts/", RedirectView.as_view(pattern_name='account_login'), name='accounts-redirect'),
    path("accounts/profile/", RedirectView.as_view(pattern_name='index'), name='accounts-redirect')
]
