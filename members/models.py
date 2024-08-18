from django.db import models
from django.contrib.auth.models import User

class Course(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    title = models.CharField(max_length=255)
    department_tag = models.CharField(max_length=255)
    department_name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    unit_min = models.CharField(max_length=5)
    unit_max = models.CharField(max_length=5)
    prereqs = models.CharField(max_length=255, null=True)
    overlap = models.CharField(max_length=255, null=True)
    same_as = models.CharField(max_length=255, null=True)
    restriction = models.CharField(max_length=255, null=True)
    coreq = models.CharField(max_length=255, null=True)

class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    tag = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name} ({self.tag})'
    
class Note(models.Model):
    # Foreign keys as to connect each note to an exisitng course and user,
    #  also makes finding each note easier as we can index by these two foreign keys
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    note = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f'Note for {self.course.title} by {self.user.username}'



# Remove these guys laterrrr
class Users(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    password = models.CharField(max_length=30)

class Member(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    birthday = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f'{self.username}'

class Student(models.Model):
    name = models.CharField(max_length=255)
    grade = models.CharField(max_length=255)
    major = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}, {self.grade}, {self.major}'