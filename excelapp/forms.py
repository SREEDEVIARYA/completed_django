from django import forms
from .models import Student
from accounts.models import CustomUser


from django import forms
from .models import Student
from accounts.models import CustomUser


class StudentForm(forms.ModelForm):

    allocated_consultant = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role="consultant"),
        empty_label="Select Consultant",
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = Student
        fields = "__all__"

        widgets = {
            "student_name": forms.TextInput(attrs={"class": "form-control"}),
            "batch_time": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "fees_pending": forms.NumberInput(attrs={"class": "form-control"}),
            "course": forms.TextInput(attrs={"class": "form-control"}),
            "mode_of_class": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show only consultant name in dropdown
        self.fields["allocated_consultant"].label_from_instance = (
            lambda obj: obj.consultant_name
        )

    def save(self, commit=True):
        student = super().save(commit=False)

        # Save consultant name in Student model
        student.allocated_consultant = self.cleaned_data[
            "allocated_consultant"
        ].consultant_name

        if commit:
            student.save()

        return student