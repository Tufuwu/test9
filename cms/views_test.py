"""
Test end to end django views.
"""
from django.urls import reverse
import pytest


pytestmark = [pytest.mark.django_db]


def test_cms_signin_redirect_to_site_signin(client):
    """
    Test that the cms/password_reset redirects users to site signin page.
    """
    response = client.get(reverse("wagtailadmin_home"), follow=True)
    assert response.template_name == "cms/home_page.html"


def test_cms_password_reset_redirect_to_site_signin(client):
    """
    Test that the cms/password_reset redirects users to site signin page.
    """
    response = client.get(reverse("wagtailadmin_password_reset"), follow=True)
    assert response.template_name == "cms/home_page.html"
