import re
from datetime import date

from flask_wtf import FlaskForm
from wtforms import (DateField, RadioField, SelectField, SelectMultipleField,
                     StringField, TextAreaField, widgets)
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError

from ..content import load_site
from ..utils import clean_phone

CLASS_CHOICES = [("", "Select class")] + [(str(n), f"Class {n}") for n in range(6, 13)]
DAY_CHOICES = [(d, d) for d in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")]
TIME_CHOICES = [("", "No preference"), ("Morning", "Morning"), ("Afternoon", "Afternoon"),
                ("Evening", "Evening")]
MODE_CHOICES = [("Offline", "Offline (in person)"), ("Online", "Online")]
GENDER_CHOICES = [("", "Prefer not to say"), ("Female", "Female"), ("Male", "Male"), ("Other", "Other")]
RELATION_CHOICES = [("", "Select relationship"), ("Mother", "Mother"), ("Father", "Father"),
                    ("Guardian", "Guardian"), ("Other", "Other")]


def _strip(value):
    return value.strip() if isinstance(value, str) else value


def indian_mobile(form, field):
    if not re.fullmatch(r"[6-9]\d{9}", clean_phone(field.data)):
        raise ValidationError("Enter a valid 10-digit mobile number.")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class AdmissionForm(FlaskForm):
    # Student
    student_name = StringField("Student full name", filters=[_strip],
                               validators=[DataRequired(), Length(2, 100)])
    date_of_birth = DateField("Date of birth", validators=[Optional()])
    gender = SelectField("Gender", choices=GENDER_CHOICES, validators=[Optional()])
    school_name = StringField("Current school", filters=[_strip],
                              validators=[DataRequired(), Length(2, 150)])
    student_class = SelectField("Current class", choices=CLASS_CHOICES,
                                validators=[DataRequired(message="Select the student's class.")])
    subjects = MultiCheckboxField("Subjects needed", choices=[],
                                  validators=[DataRequired(message="Select at least one subject.")])
    # Parent / guardian
    parent_name = StringField("Parent or guardian name", filters=[_strip],
                              validators=[DataRequired(), Length(2, 100)])
    relationship = SelectField("Relationship with student", choices=RELATION_CHOICES,
                               validators=[DataRequired(message="Select the relationship.")])
    mobile = StringField("Mobile number", filters=[_strip], validators=[DataRequired(), indian_mobile])
    alt_mobile = StringField("Alternate number", filters=[_strip], validators=[Optional(), indian_mobile])
    email = StringField("Email address", filters=[_strip],
                        validators=[Optional(), Email(), Length(max=120)])
    # Preferences
    mode = RadioField("Class type", choices=MODE_CHOICES,
                      validators=[DataRequired(message="Choose online or offline.")])
    preferred_days = MultiCheckboxField("Preferred days", choices=DAY_CHOICES, validators=[Optional()])
    preferred_time = SelectField("Preferred time", choices=TIME_CHOICES, validators=[Optional()])
    notes = TextAreaField("Anything else we should know?", filters=[_strip],
                          validators=[Optional(), Length(max=1000)])
    # Honeypot: real visitors never see or fill this.
    website = StringField("Leave this field empty", validators=[Optional()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subjects.choices = [(s, s) for s in load_site()["subjects"]]

    def validate_date_of_birth(self, field):
        if field.data and not (date(date.today().year - 30, 1, 1) < field.data < date.today()):
            raise ValidationError("Enter a valid date of birth.")


class ContactForm(FlaskForm):
    name = StringField("Your name", filters=[_strip], validators=[DataRequired(), Length(2, 100)])
    phone = StringField("Mobile number", filters=[_strip], validators=[DataRequired(), indian_mobile])
    email = StringField("Email address", filters=[_strip],
                        validators=[Optional(), Email(), Length(max=120)])
    message = TextAreaField("Message", filters=[_strip], validators=[DataRequired(), Length(5, 1500)])
    website = StringField("Leave this field empty", validators=[Optional()])
