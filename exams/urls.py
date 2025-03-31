"""URLs for exams app"""
from django.conf.urls import url

from exams.views import (
    PearsonCallbackRedirectView,
    PearsonSSO,
)

urlpatterns = [
    url(
        r'^pearson/(?P<status_code>success|error|timeout|logout)/?$',
        PearsonCallbackRedirectView.as_view(),
        name='pearson_callback'
    ),
    url(r'^api/v0/pearson/sso/$', PearsonSSO.as_view(), name='pearson_sso_api'),
]
