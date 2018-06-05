import json

from django import forms
from django.forms import ModelForm, Form, BooleanField
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User 

from .models import Question, QuestionSet

class QuestionForm(ModelForm):

    class Meta:
        model = Question
        fields = ('text', 'choices')

    def clean_choices(self):
        choices  = self.data['choices']
        return json.dumps(choices)
        
class QuestionSetForm(ModelForm):

    class Meta:
        model = QuestionSet
        fields = ('questions', )
        
class RegForm(Form):
    username = forms.CharField()
    password = forms.CharField()
    
    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']).exists():
            raise ValidationError('Already exists.')
        return self.cleaned_data['username']
    
def get_test_form_class(choices):

    class BoolFieldsForm(Form):
        pass
    
    for index, choice in enumerate(choices):
        # [ak] a little bit durty, but fits for this task...
        BoolFieldsForm.base_fields[f'field_{index}'] = BooleanField(required=False, label=choice['text'])
        
    class DataForm(BoolFieldsForm):
        
        def clean(self):
            if not any(self.cleaned_data.values()):
                raise ValidationError('At least one should be checked')
            if all(self.cleaned_data.values()):
                raise ValidationError('All cannot be checked')
            return super().clean()
            
    return DataForm
    
