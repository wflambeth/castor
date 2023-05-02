from django import forms

class TitleForm(forms.Form):
    class Meta:
        fields = ('title')
    
    title = forms.CharField(max_length='100', required=True)
