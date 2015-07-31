from django import forms
from hx_lti_assignment.models import Assignment, AssignmentTargets
from crispy_forms.helper import FormHelper
from django.forms.models import modelformset_factory, inlineformset_factory
from crispy_forms.layout import Layout, Fieldset, Div, Field, HTML
from crispy_forms.bootstrap import TabHolder, Tab
import re

class AssignmentForm(forms.ModelForm):

	def __init__(self, *args, **kwargs):
		super(AssignmentForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			TabHolder(
				Tab(
					'Assignment Information',
					'assignment_name',
					Field('course', css_class="selectpicker", data_live_search="true"),
				),
				Tab(
					'Annotation Database Settings',
					'annotation_database_url',
					'annotation_database_apikey',
					'annotation_database_secret_token',
				),
				Tab(
					'Annotation Table Settings',
					'include_instructor_tab',
					Field('default_tab', css_class="selectpicker"),
					'pagination_limit',
				),
				Tab(
					'Annotator Settings',
					Fieldset(
						"Colored Highlights",
						'allow_highlights',
						'highlights_options',
					),
					Fieldset(
						"Turn Settings On/Off",
						'allow_touch',
						'allow_flags',
					),
				),
			)
		)

	def clean_annotation_database_url(self):
		# from http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python
		url = self.cleaned_data['annotation_database_url']
		urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', url)
		
		if len(urls) == 0:
			raise forms.ValidationError("You did not type in a URL for the database!")
		
		return url

	class Meta:
		model = Assignment


class AssignmentTargetsForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AssignmentTargetsForm, self).__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_tag = False
		self.helper.layout = Layout(
			Div(
				'target_object',
				'order',
				'target_external_css'
			),
		)

	class Meta:
		model = AssignmentTargets

AssignmentTargetsFormSet = inlineformset_factory(Assignment, AssignmentTargets, can_delete=True)

class NoFormTagCrispyFormMixin(object):
    @property
    def helper(self):
        if not hasattr(self, '_helper'):
            self._helper = FormHelper()
            self._helper.form_tag = False
        return self._helper