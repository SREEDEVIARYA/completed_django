from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


# ✅ Consultant/Admin Register Form
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class ConsultantRegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            "emp_id",
            "consultant_name",
            "company_email",
            "role",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Display only Consultant role
        self.fields["role"].choices = [
            ("consultant", "Consultant"),
        ]

        self.fields["role"].widget.attrs.update({
            "class": "form-control"
        })

    def save(self, commit=True):
        user = super().save(commit=False)

        # Always save as Consultant
        user.role = "consultant"

        if commit:
            user.save()

        return user
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class AdminRegisterForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = [
            "emp_id",
            "consultant_name",
            "company_email",
            "role",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Display only Admin role in dropdown
        self.fields["role"].choices = [
            ("admin", "Admin"),
        ]

        self.fields["role"].widget.attrs.update({
            "class": "form-control"
        })

    def save(self, commit=True):
        user = super().save(commit=False)

        # Always save as Admin
        user.role = "admin"

        if commit:
            user.save()

        return user

# ✅ Student Register Form
class StudentRegisterForm(UserCreationForm):

    reg_no = forms.CharField(
        max_length=50,
        label="Register Number",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    student_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    student_email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = CustomUser
        fields = ["reg_no", "student_name", "student_email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)

        user.emp_id = self.cleaned_data["reg_no"]
        user.student_name = self.cleaned_data["student_name"]
        user.student_email = self.cleaned_data["student_email"]
        user.role = "student"

        if commit:
            user.save()

        return user
from django import forms
from .models import Feedback

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        exclude = ["student", "submitted_at"]

        widgets = {
            "date_of_join": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control"
                },
                format="%Y-%m-%d"
            ),
            "overall_experience": forms.RadioSelect(),
            "content_relevance": forms.RadioSelect(),
            "quality_materials": forms.RadioSelect(),
            "trainer_encouragement": forms.RadioSelect(),
            "mode_of_delivery": forms.RadioSelect(),

            "class_started_on_time": forms.RadioSelect(),
            "skill_enhancement": forms.RadioSelect(),
            "confident_apply_skills": forms.RadioSelect(),
            "recording_uploaded": forms.RadioSelect(),

            "tools_helpful": forms.RadioSelect(),
            "duration_sufficient": forms.RadioSelect(),
            "program_pace": forms.RadioSelect(),

            "recommend_program": forms.RadioSelect(),
            "program_rating": forms.RadioSelect(),

            "improvement_suggestion": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "future_topics": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }