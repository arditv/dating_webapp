from django.contrib import admin
from .models import *

class ProfileAdmin(admin.ModelAdmin):
    fields = ('image','dob')
    ordering = ['dob']

class MemberAdmin(admin.ModelAdmin):
    fields = ('username','password','email', 'profile', 'likes', 'gender', 'hobbies')
    list_display = ('username','password','likes_count', 'liked_count')
    ordering = ['username']


class HobbyAdmin(admin.ModelAdmin):
    fields = ('name','desc')
    ordering = ['name']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Hobby, HobbyAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Gender)
