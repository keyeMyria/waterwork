# -*- coding: utf-8 -*-

from django import forms

from .models import Personalized


class logoPagesPhotoForm(forms.ModelForm):
    class Meta:
        model = Personalized
        fields = ('logoPagesPhoto',  )