from django import forms
from django.forms import ModelForm

from .models import Comment


class CommentForm(ModelForm):
    url = forms.URLField(label='Url', required=False)
    email = forms.EmailField(label='Email', required=True)
    name = forms.CharField(
        label='Fullname',
        widget=forms.TextInput(
            attrs={
                'value': "",
                'size': "30",
                'maxlength': "245",
                'aria-required': 'true'}))
    parent_comment_id = forms.IntegerField(
        widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['body']
