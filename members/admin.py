from django.contrib import admin
from .models import *

# Register your models here.

# Get rid of member and student at some point, yuck!!!
class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password')

class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade', 'major')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tag')

class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'department_tag', 'department_name', 'unit_min', 'unit_max', 'description')

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'password')

admin.site.register(Member, MemberAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Users, UserAdmin)
