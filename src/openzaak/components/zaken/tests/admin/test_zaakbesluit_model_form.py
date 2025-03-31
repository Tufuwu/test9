# SPDX-License-Identifier: EUPL-1.2
# Copyright (C) 2020 Dimpact
from django import forms
from django.test import TestCase

from openzaak.components.zaken.admin import ZaakBesluitForm


class TestZaakBesluitForm(TestCase):
    def test_zaakbesluit_form_clean_does_not_throw_exception_if_besluit_is_given(self):
        form = ZaakBesluitForm()
        form.cleaned_data = {
            "_besluit": 1,
        }
        try:
            form.clean()
        except forms.ValidationError:
            self.fail("Exception was raised in clean function when it should not have")

    def test_zaakbesluit_form_clean_does_not_throw_exception_if_besluit_url_is_given(
        self,
    ):
        form = ZaakBesluitForm()
        form.cleaned_data = {
            "_besluit_url": "https://testserver",
        }
        try:
            form.clean()
        except forms.ValidationError:
            self.fail("Exception was raised in clean function when it should not have")

    def test_zaakbesluit_form_clean_throws_exception_if_besluit_and_besluit_url_are_not_given(
        self,
    ):
        form = ZaakBesluitForm()
        form.cleaned_data = {}
        with self.assertRaises(forms.ValidationError):
            form.clean()
