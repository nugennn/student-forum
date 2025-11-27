from django import forms
from .models import Profile,Position
from martor.fields import MartorFormField

class EditProfileForm(forms.ModelForm):
	full_name = forms.CharField(
	    disabled=True, 
	    required=False, 
	    help_text='Full name is set by the admin and cannot be changed here.',
	    widget=forms.TextInput(attrs={'class': 'textinput textInput form-control'})
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Set the initial full_name from the instance
		if self.instance:
			self.fields['full_name'].initial = self.instance.full_name or ''
			self.fields['full_name'].widget.attrs['value'] = self.instance.full_name or ''
		
		# Auto-populate title field based on user email domain
		if self.instance and self.instance.user:
			email = self.instance.user.email
			if email.endswith('@khwopa.edu.np'):
				self.fields['title'].initial = '@khwopa.edu.np'
				self.fields['title'].widget.attrs['readonly'] = True
				self.fields['title'].help_text = 'Automatically set for Teachers'
			elif email.endswith('@khec.edu.np'):
				self.fields['title'].initial = '@khec.edu.np'
				self.fields['title'].widget.attrs['readonly'] = True
				self.fields['title'].help_text = 'Automatically set for Students'

	class Meta:
		model = Profile
		fields = ['profile_photo', 'full_name', 'location', 'title', 'about_me',
			  'website_link', 'twitter_link', 'github_link']

class EmailForm(forms.Form):
	name = forms.CharField(max_length=25)
	email = forms.EmailField()
	review = MartorFormField()

class PositionCreateForm(forms.ModelForm):

	class Meta:
		model = Position
		fields = ['company_name','title']


class EditEmailForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ['email']