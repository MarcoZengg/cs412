"""
File: forms.py
Author: Xiankun Zeng (xiankz23@bu.edu)
Description: Form classes for project interactions.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import GameSession, Round


class StartGameSessionForm(forms.ModelForm):
    """Collect basic settings to start a new game session."""

    class Meta:
        model = GameSession
        fields = ["difficulty", "total_rounds"]
        widgets = {
            "difficulty": forms.Select(
                attrs={"class": "session-difficulty-select"}
            ),
            "total_rounds": forms.NumberInput(
                attrs={"class": "session-rounds-input", "min": 1, "max": 50}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["difficulty"].initial = "mixed"


class CreateAccountForm(UserCreationForm):
    """Username/password account creation form for the project app."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")


class SubmitGuessForm(forms.ModelForm):
    """Collect guessed coordinates for a round submission."""

    class Meta:
        model = Round
        fields = ["guess_latitude", "guess_longitude"]

    def __init__(self, *args, **kwargs):
        """Require both coordinate fields for a valid guess submission."""
        super().__init__(*args, **kwargs)
        self.fields["guess_latitude"].required = True
        self.fields["guess_longitude"].required = True

    def clean(self):
        """Validate both coordinates are present before saving."""
        cleaned_data = super().clean()
        guess_latitude = cleaned_data.get("guess_latitude")
        guess_longitude = cleaned_data.get("guess_longitude")

        if guess_latitude is None or guess_longitude is None:
            raise forms.ValidationError("Please provide both latitude and longitude.")
        return cleaned_data
