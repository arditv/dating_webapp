from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, Http404, JsonResponse, QueryDict, HttpResponseRedirect
from django.template import RequestContext, loader
from mainapp.models import Member, Profile, Hobby, Gender
from django.contrib.auth.hashers import make_password
from django.core import serializers
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
if 'makemigrations' not in sys.argv and 'migrate' not in sys.argv:
    from .forms import LoginForm, RegisterForm, EditForm
from django.core.mail import send_mail
from django.urls import reverse
import datetime as D

appname = 'MatchMe'
#renders the index template with the appname as context
def index(request):
    context = { 'appname': appname }
    return render(request,'mainapp/index.html',context)
#checks if the session has a username passed to it and returns the logged in member object as an argument. It used to check before a view is called whether or not the client is logged in or not
def loggedin(view):
    def mod_view(request):
        if 'username' in request.session:
            username = request.session['username']
            try: user = Member.objects.get(username=username)
            except Member.DoesNotExist: raise Http404('Member does not exist')
            return view(request, user)
        else:
            return render(request,'mainapp/not-logged-in.html',{})
    return mod_view
#used for logging in the user using django forms
def login(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = LoginForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try: member = Member.objects.get(username=username)
            except Member.DoesNotExist: raise ValidationError(('Username DoesNotExist'), code='DoesNotExist')
            if member.check_password(password):
                # remember user in session variable
                request.session['username'] = username
                request.session['password'] = password
                context = {
                   'appname': appname,
                   'username': username,
                   'profile': member.profile,
                   'loggedin': True
                }
                response = render(request, 'mainapp/matches.html', context)

                # remember last login in cookie
                now = D.datetime.utcnow()
                max_age = 365 * 24 * 60 * 60  #one year
                delta = now + D.timedelta(seconds=max_age)
                format = "%a, %d-%b-%Y %H:%M:%S GMT"
                expires = D.datetime.strftime(delta, format)
                #set the cookie cookie in context so the user will be logged in for a year
                response.set_cookie('last_login',now,expires=expires)

                return response
            else:
                return render(request,'mainapp/wrongpassword.html',{})
    else:
        form = LoginForm()

    return render(request, 'mainapp/login.html', {'form': form})

def signup(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST, request.FILES)
        # check whether it's valid:
        if form.is_valid():
            #cleans the data from the form and creates a new profile and member record in the database.
            u = form.cleaned_data['username']
            p = form.cleaned_data['password']
            em = form.cleaned_data['email']
            hobs = form.cleaned_data['hobbies']
            helicopter = form.cleaned_data['gender']
            dateob = form.cleaned_data['dob']
            image_file = form.cleaned_data['file']
            hobbiesar = []
            for x in hobs:
                hobby = Hobby.objects.get(pk = x)
                hobbiesar.append(hobby)
            gend = Gender.objects.get(pk = helicopter)
            prof = Profile(image = image_file, dob=dateob)
            prof.save()
            user = Member(username = u,
                         email = em,
                          profile = prof,
                          gender =gend
                          )
            user.set_password(p)
            user.save()
            user.hobbies.set(hobbiesar)
            return HttpResponseRedirect('/login')
    else:
        form = RegisterForm()

    return render(request, 'mainapp/createAccount.html', {'form': form})

#renders the editprofile template page to edit the user
@loggedin
def editprofilepage(request, user):
    context = { 'appname': appname }
    return render(request,'mainapp/editprofile.html',context)
#this passes the request and current logged in user to the form so the current information can be displayed in textboxes

@loggedin
def editprofile(request, user):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        print(user.username)
        form = EditForm(request.POST, request.FILES, data = user)
        # check whether it's valid:
        if form.is_valid():
            #cleans data and sets the current user's details
            em = form.cleaned_data['email']
            hobs = form.cleaned_data['hobbies']
            helicopter = form.cleaned_data['gender']
            if form.cleaned_data['file'] != None:
                image_file = form.cleaned_data['file']
                user.profile.image = image_file
                user.profile.save()
            hobbiesar = []
            for x in hobs:
                hobby = Hobby.objects.get(pk = x)
                hobbiesar.append(hobby)
            gend = Gender.objects.get(pk = helicopter)
            user.email = em
            user.gender = gend
            user.save()
            user.hobbies.set(hobbiesar)
            return HttpResponseRedirect('/profile')
    else:
        form = EditForm(data = user)

    context = {
        'appname': appname,
        'username': user.username,
        'profile' : user.profile,
        'loggedin': True,
        'form': form
    }
    return render(request, 'mainapp/editprofile.html', context)
#passes basic context before rendering the matches template
@loggedin
def matches(request, user):
    context = {
        'appname': appname,
        'username': user.username,
        'profile' : user.profile,
        'loggedin': True
    }
    return render(request,'mainapp/matches.html',context)
#renders the profile template and passes all the information about the user to the template in the context
@loggedin
def userProfile(request,user):
    arr = []
    for x in user.hobbies.all():
        arr.append(x.name)
    context = {
        'appname': appname,
        'user': user,
        'profile' : user.profile,
        'loggedin': True,
        'hobbies' : arr
    }
    return render(request,'mainapp/profile.html',context)
#clears cookies and logs out the user
@loggedin
def logout(request, user):
    request.session.flush()
    context = { 'appname': appname }
    return render(request,'mainapp/logout.html', context)
# checks which hobbies are common with other users and returns the sorted list of users who have the most hobbies in common with the logged in user.
# It also returns whether or not the logged in user liked a particular member.
@loggedin
def getUsersWithSameHobbies(request, user):
    userlikes = []
    for x in user.likes.all():
        userlikes.append(x)
    userhobarr = []
    for x in user.hobbies.all():
        userhobarr.append(x.name)
    json_res = []
    for x in Member.objects.all():
        if x != user:
            memberhobarr = []
            for y in x.hobbies.all():
                memberhobarr.append(y.name)
            listofcommonhobbies = []
            for z in set(userhobarr).intersection(memberhobarr):
                listofcommonhobbies.append(z)
            if x in user.likes.all():
                json_obj = dict(
                    id = x.id,
                    name = x.username,
                    commonhno = len(set(userhobarr).intersection(memberhobarr)),
                    commonh = listofcommonhobbies,
                    gender = x.gender.name,
                    dob = str(x.profile.dob),
                    liked = True
                )
            else:
                json_obj = dict(
                    id = x.id,
                    name = x.username,
                    commonhno = len(set(userhobarr).intersection(memberhobarr)),
                    commonh = listofcommonhobbies,
                    gender = x.gender.name,
                    dob = str(x.profile.dob),
                    liked = False
                )
            json_res.append(json_obj)
    json_res.sort(key=lambda x: x['commonhno'], reverse=True)
    return JsonResponse(json_res, safe=False)
#used for sending email notifications about the logged in user liking other users and adding members to the liked field
@loggedin
def likeUser(request, user):
    if request.method == "POST":
        if 'likeID' in request.POST:
            likeID = request.POST['likeID']
            likes = []
            for x in user.likes.all():
                likes.append(x)
            likedmember = Member.objects.get(pk = likeID)
            likes.append(likedmember)
            user.likes.set(likes)
            send_mail(
                        user.username + ' likes you!',
                        'Lorem ipsum dolor sit amet this user: ' + user.username + ' likes you!',
                        str(user.email),
                        [str(likedmember.email)],
                        fail_silently=False,
                    )
        else:
            dislikeID = request.POST['dislikeID']
            dislikedmember = Member.objects.get(pk = dislikeID)
            likes = []
            for x in user.likes.all():
                if x != dislikedmember:
                    likes.append(x)
            user.likes.set(likes)
            send_mail(
                        user.username + ' stopped liking you! :(',
                        'Lorem ipsum dolor sit amet this user: ' + user.username + ' hates you!',
                        str(user.email),
                        [str(dislikedmember.email)],
                        fail_silently=False,
                    )
        return JsonResponse("", safe=False)

#username validation
def checkuser(request):
    if 'username' in request.POST:
        try:
            member = Member.objects.get(username=request.POST['username'])
        except Member.DoesNotExist:
            if request.POST['page'] == 'login':
                return HttpResponse("<span class='taken'>&nbsp;&#x2718; Invalid username</span>")
            if request.POST['page'] == 'createAccount':
                return HttpResponse("<span class='available'>&nbsp;&#x2714; This username is available</span>")
    if request.POST['page'] == 'login':
        return HttpResponse("<span class='available'>&nbsp;&#x2714; Valid username</span>")
    if request.POST['page'] == 'register':
        return HttpResponse("<span class='taken'>&nbsp;&#x2718; This username is taken</span>")
    return HttpResponse("<span class='taken'>&nbsp;&#x2718; Invalid request</span>")
