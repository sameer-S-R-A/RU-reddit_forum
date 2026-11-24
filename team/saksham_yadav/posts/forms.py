from django import forms
class PostForm(forms.Form):
    community = forms.ChoiceField()
    post_type = forms.ChoiceField(choices=[("text", "Text"), ("link", "Link"), ("image", "Image")])
    title = forms.CharField(max_length=300)
    body = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 7, "placeholder": "What do you want to discuss?"}))
    link_url = forms.URLField(required=False)
    image = forms.ImageField(required=False)

    def __init__(self, *args, communities=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["community"].choices = [(item["id"], f"r/{item['name']}") for item in (communities or [])]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("post_type") == "link" and not cleaned.get("link_url"):
            self.add_error("link_url", "Add a link for a link post.")
        if cleaned.get("post_type") == "image" and not cleaned.get("image"):
            self.add_error("image", "Choose an image for an image post.")
        return cleaned
