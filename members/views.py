# from django.shortcuts import render # they told me to get rid of this in the templates tutorial because template.loader has its own form of render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Department, Course, Note
from .connect import connect

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

import re

def catalog(request):
    template = loader.get_template('catalog.html')
    context = {
        'allDepartments' : [(d['name'], d['tag']) for d in Department.objects.all().values()], # query sets work like dictionaries
        'logged_in' : request.session.get('username', ''),
    }

    return HttpResponse(template.render(context, request))

def courses(request, department):
    template = loader.get_template('catalog.html')
    departments = [(d['name'], d['tag']) for d in Department.objects.all().values()]

    # Chat Function, thank you, i will learn regex at a later point...
    #  Explanation for some stuff:
    #  
    def html_courses(text):
        for name, tag in departments:
            # \s = escape character for space, [A-Z]? means possible character betwen A-Z
            # \d+ = escape character for any positive digit (im pretty sure)
            pattern = fr'(?<!\w)({re.escape(tag)} [A-Z]?[A-Z]?\d+[A-Z]?[A-Z]?)(?!\w)'
            text = re.sub(pattern, lambda match: f'<span class="course-popup">{match.group(0)}</span>', text)
        return text
    
    def add_courses():
        for c in connect():
            if len(c['units']) == 1:
                c['units'] = [c['units'][0], c['units'][0]]
            
            fields_to_process = ['description', 'prerequisite_text', 'overlap', 'same_as', 'corequisite', 'restriction']
            
            for field in fields_to_process:
                c[field] = html_courses(c[field])
            
            course = Course(c['id'], c['title'], c['department'], c['department_name'], 
                            c['description'], c['units'][0], c['units'][1], c['prerequisite_text'], 
                            c['overlap'], c['same_as'], c['restriction'], c['corequisite'])
            course.save()
    
    def del_courses():
        for c in Course.objects.all():
            c.delete()

    # del_courses()
    # add_courses()
    
    # Grab user notes if logged in
    logged_in = request.session.get('username', '')
    user_notes = '' 
    if logged_in:
        user_id = [u['id'] for u in User.objects.all().values() if u['username'] == logged_in][0]
        user_notes = [(n['course_id'], n['note']) for n in Note.objects.all().values() if n['user_id'] == user_id]
    
    context = {
        'allCourses' : Course.objects.all().values(), # query set grabbed from the sql
        'department' : department, # this value is obtained from the URL, as seen in urls.py as <str:department>, and stored in parameter
        'allDepartments' : departments, # Returns a list of all departments as tuples (name, tag) 
        'logged_in' : logged_in,
        'user_notes' : user_notes,
    }
    
    return HttpResponse(template.render(context, request))

def about(request):
    template = loader.get_template('about.html')

    context = {
        'name' : request.session.get('username', 'Guest'),
        'pass' : request.session.get('password', 'Password'),
        'logged_in' : request.session.get('username', '')
    }

    return HttpResponse(template.render(context, request))

def home(request):
    template = loader.get_template('home.html')

    context = {
        'logged_in' : request.session.get('username', ''),
        'temp': 'temp',
    }

    return HttpResponse(template.render(context, request))

def account(request):
    template = loader.get_template('account.html')

    if request.method == 'POST':
        logout(request)
        return redirect('catalog')

    context = {
        'logged_in' : request.session.get('username', ''),
    }

    return HttpResponse(template.render(context, request))

def login_user(request):
    template = loader.get_template('login.html')
    path = str(request.path[1:-1])
    username = ''
    password = ''
    repassword = ''
    users = [(u['username'], u['password']) for u in User.objects.all().values()]
    usernames = [u[0] for u in users]
    status = False
    incorrectPass = False


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        repassword = request.POST.get('repassword')
        user = authenticate(request, username=username, password=password) 
        
        # Login
        if path == 'login':
            if user is not None:
                login(request, user)
                request.session['username'] = user.username
                request.session['password'] = user.password
                status = True
            else:
                for u, p in users:
                    if username == u:
                        if password != p:
                            incorrectPass = True

        # Sign Up
        if password == repassword and username not in usernames and path == 'signup':
            new_user = User.objects.create_user(username, '', password)
            new_user.save()
            
            user = authenticate(request, username=username, password=password) 
            login(request, user)
            request.session['username'] = user.username
            request.session['password'] = user.password

            status = True


    # For login page, required because im lazy and used same html for login and signup
    if password and not repassword:
        repassword = password

    context = {
        'type' : path,
        'username' : username,
        'password' : password,
        'repassword' : repassword,
        'users' : usernames,
        'status' : status,
        'incorrectPass' : incorrectPass,
        'logged_in' : request.session.get('username', ''),
    }

    return HttpResponse(template.render(context, request))

@login_required
@csrf_exempt
def save_note(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        note_content = request.POST.get('note_content', '')
        course_id = request.POST.get('course_id')
        course = Course.objects.get(id=course_id)
        note, created = Note.objects.get_or_create(user=request.user, course=course)
        note.note = note_content
        note.save()
        return JsonResponse({'status': 'success', 'message': 'Note saved'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def popup(request):
    # request.headers.get('x-requested-with') == 'XMLHttpRequest' is equal to is_ajax() since it was deprecated
    if request.GET.get('course_id') and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        course_id = request.GET.get('course_id').replace(' ', '')
        course = Course.objects.get(id=course_id)

        # HTML Creation
        units = f'{course.unit_min}'
        if course.unit_min != course.unit_max:
            units += f'-{course.unit_max}'

        html = f"""
            <h2 style="margin-top: 7px">
                <span class="course-title id">{course.id}</span> - 
                <span class="course-title name">
                    {course.title}. {units} units
                </span>
            </h2>
            <div class="course-card-front">                
                <p>{course.description}</p>
            """

        html += f'<p><strong>Corequisite:</strong> {course.coreq}</p>' if course.coreq else ''
        html += f'<p><strong>Prerequisite:</strong> {course.prereqs}</p>' if course.prereqs else ''
        html += f'<p>Same as {course.same_as}</p>' if course.same_as else ''
        html += f'<p>Overlaps with {course.overlap}</p>' if course.overlap else ''
        html += f'<p><strong>Resriction:</strong> {course.restriction}</p>' if course.restriction else ''
        html += '</div>'

        response_data = {
            'html': html
        }

        return JsonResponse(response_data)
    return JsonResponse({'error': 'Invalid Request'}, status=400)