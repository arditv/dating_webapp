from django import forms
from django.contrib.admin import widgets
from mainapp.models import Member, Profile, Hobby, Gender
import datetime as D

# Login form containing username and password
class LoginForm(forms.Form):
    username = forms.CharField(max_length = 20, widget=forms.TextInput(attrs={'placeholder': "Username", "class" : "loginusername"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

# Register Form consisting of username, password, email, dateofbirth, profile image, gender and list of hobbies
class RegisterForm(forms.Form):
    # gets list of gender from database
    genders=Gender.objects.all()
    GENDARR = []
    for x in genders:
        GENDARR.append((x.pk,x.name))

    # gets list of hobbies from database

    # ensures only users above 18 years old are allowed to register
    now = D.datetime.utcnow()
    age18 =D.timedelta(seconds=365 * 24 * 60 * 60 * 17)
    delta = now - age18
    format = "%Y"
    minage = D.datetime.strftime(delta, format)

    username = forms.CharField(max_length = 20, widget=forms.TextInput(attrs={'placeholder': "Username", "class" : "registerusername"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    email = forms.CharField(widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))
    dob = forms.DateField(widget=forms.SelectDateWidget(years=range(1910,int(minage)),attrs={'class': 'Date of birth'}))
    file = forms.ImageField(widget=forms.FileInput(attrs={'class': 'ProfilePic'}))
    gender = forms.ChoiceField(choices=GENDARR,widget=forms.Select(attrs={'class': 'Gender'}))

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        hobo=Hobby.objects.all()
        HOBBARR = []
        for x in hobo:
            HOBBARR.append((x.pk,x.name))
        self.fields['hobbies'] = forms.MultipleChoiceField(choices=HOBBARR,widget=forms.CheckboxSelectMultiple(attrs={'class': 'hobbies'}))

# edit profile form to change user details such as email, profile image, gender and list of hobbies
class EditForm(forms.Form):

    def __init__(self, *args, **kwargs):
        genders=Gender.objects.all()
        GENDARR = []
        for x in genders:
            GENDARR.append((x.pk,x.name))

        hobo=Hobby.objects.all()
        HOBBARR = []
        for x in hobo:
            HOBBARR.append((x.pk,x.name))

        now = D.datetime.utcnow()
        age18 = D.timedelta(seconds=365 * 24 * 60 * 60 * 17)
        delta = now - age18
        format = "%Y"
        minage = D.datetime.strftime(delta, format)
        user = kwargs.pop('data', None)

        # gets current user hobbies and displayed it as checked list
        selectedhobbies = []
        for x in user.hobbies.all():
            selectedhobbies.append(x.pk)

        super(EditForm, self).__init__(*args, **kwargs)
        self.fields['email'] = forms.CharField(required=False,widget=forms.EmailInput(attrs={'value': user.email}))
        self.fields['file'] = forms.ImageField(required=False,widget=forms.FileInput(attrs={'class': 'ProfilePic'}))
        self.fields['gender'] = forms.ChoiceField(required=False,choices=GENDARR,initial=user.gender.pk ,widget=forms.Select(attrs={'autocomplete':'off'}))
        self.fields['hobbies'] = forms.MultipleChoiceField(required=False,initial=selectedhobbies,choices=HOBBARR,widget=forms.CheckboxSelectMultiple(attrs={}))
