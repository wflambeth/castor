from django import forms

class TitleForm(forms.Form):
    class Meta:
        fields = ('title', 'sched_id')
    
    sched_id = forms.IntegerField(widget = forms.HiddenInput(), required=True)
    title = forms.CharField(max_length='100', required=True)
