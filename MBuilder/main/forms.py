from django import forms


class SchemGenerateForm(forms.Form):
    prompt = forms.CharField(widget=forms.Textarea, label="Your prompt")
