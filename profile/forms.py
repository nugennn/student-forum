from django import forms
from .models import Profile,Position
from martor.fields import MartorFormField

class EditProfileForm(forms.ModelForm):
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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
		fields = ['profile_photo','full_name','location','title','about_me',
					'website_link','twitter_link','github_link',
							'not_to_Display_Full_name']

class EmailForm(forms.Form):
	name = forms.CharField(max_length=25)
	email = forms.EmailField()
	review = MartorFormField()

class PositionCreateForm(forms.ModelForm):

	class Meta:
		model = Position
		fields = ['company_name','title']

JOB_TYPE_CHOICES = [

    ('FULL_TIME', 'Full Time'),
    ('CONTRCT', 'Contract'),
    ('InternShip', 'InternShip'),

]


class EditJobPrefrences(forms.ModelForm):
	# job_type = forms.MultipleChoiceField(choices=JOB_TYPE_CHOICES, widget=forms.CheckboxSelectMultiple())

	class Meta:
		model = Profile
		fields = ['min_expierence_level',
					'max_expierence_level','job_type',
						'job_search_status','phone_number']
		widgets = {
			'job_search_status': forms.RadioSelect(),
			# 'job_type': forms.CheckboxSelectMultiple(),
		}

			

class EditEmailForm(forms.ModelForm):

	class Meta:
		model = Profile
		fields = ['email']