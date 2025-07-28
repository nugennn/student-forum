from django import forms
from .models import Post, Profile

class PostForm(forms.ModelForm):
	body = forms.CharField(required=True, 
		widget=forms.widgets.Textarea(
			attrs={
			"placeholder": "Ask a question or share an update",
			"class":"form-control",
			}
			),
			label="",
		)

	class Meta:
		model = Post
		exclude = ("user", "likes",)