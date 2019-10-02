from django.urls import path
from mainapp import views
from django.views.static import serve

urlpatterns = [
  path('', views.index, name='index'),


  # signup page
  path('createAccount/', views.signup, name='createAccount'),

    # login page
    path('login', views.login, name='login'),

    #profile page
    path('profile/', views.userProfile, name='profile'),

    # matches page (Main page of app)
    path('matches/', views.matches, name='matches'),

    #log out page
    path('logOut/', views.logout, name='logOut'),

    # returns list of users with similar hobbies
    path('getUsersWithSameHobbies/', views.getUsersWithSameHobbies, name='getUsersWithSameHobbies'),

    # edit profile page
    path('editprofile/', views.editprofile, name='editprofile'),

    # sends notifications to user when they are liked or disliked
    path('likeUser/', views.likeUser, name='likeUser'),

     # check if username is taken in database
    path('checkuser/', views.checkuser, name='checkuser'),
]
