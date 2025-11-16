from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field
from .models import Tag


class TagSearchForm(forms.Form):
    tag_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tag name (e.g., python, javascript, startup)',
            'autocomplete': 'off',
            'id': 'tag-input'
        }),
        label='Tag Name'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('tag_name', css_class='mb-3'),
            Submit('submit', 'Start Crawling', css_class='btn btn-primary btn-lg')
        )
    
    def clean_tag_name(self):
        tag_name = self.cleaned_data['tag_name'].strip().lower()
        if not tag_name:
            raise forms.ValidationError("Tag name cannot be empty.")
        return tag_name


class BlogSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search blogs by title, content, or author...'
        }),
        label='Search'
    )
    
    tag = forms.ModelChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        empty_label="All Tags",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Filter by Tag'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Field('search_query', css_class='mb-2'),
            Field('tag', css_class='mb-2'),
            Submit('submit', 'Search', css_class='btn btn-outline-primary')
        )