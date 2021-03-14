from django import forms

from .models import Post

class PostForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)
    
    class Meta:
        model = Post
        fields = ['group', 'text']
