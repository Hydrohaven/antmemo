# from django.shortcuts import render # they told me to get rid of this in the templates tutorial because template.loader has its own form of render
from django.http import HttpResponse, JsonResponse
from django.template import loader
from .models import Department, Course, Note
from .connect import connect

from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

def catalog(request):
    template = loader.get_template('catalog.html')
    context = {
        'allDepartments' : [(d['name'], d['tag']) for d in Department.objects.all().values()], # query sets work like dictionaries
        'logged_in' : request.session.get('username', ''),
    }

    return HttpResponse(template.render(context, request))

def courses(request, department):
    template = loader.get_template('catalog.html')
    
    def add_courses():
        for c in connect():
            if len(c['units']) == 1:
                c['units'] = [c['units'][0], c['units'][0]]
            
            course = Course(id=c['id'], title=c['title'], department_tag=c['department'], department_name=c['department_name'], description=c['description'], unit_min=c['units'][0], unit_max=c['units'][1], prereqs=c['prerequisite_text'], overlap=c['overlap'], same_as=c['same_as'], restriction=c['restriction'], coreq=c['corequisite'])
            course.save()
    
    def del_courses():
        for c in Course.objects.all():
            c.delete()

    # del_courses()
    # add_courses()

    messages.success(request, 'Note saved successfully!')
    
    # Grab user notes if logged in
    logged_in = request.session.get('username', '')
    user_notes = ''
    if logged_in:
        user_id = [u['id'] for u in User.objects.all().values() if u['username'] == logged_in][0]
        user_notes = [(n['course_id'], n['note']) for n in Note.objects.all().values() if n['user_id'] == user_id]
    
    context = {
        'allCourses' : Course.objects.all().values(), # query set grabbed from the sql
        'department' : department, # this value is obtained from the URL, as seen in urls.py as <str:department>, and stored in parameter
        'allDepartments' : [(d['name'], d['tag']) for d in Department.objects.all().values()], # Returns a list of all departments as tuples (name, tag) 
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