from django.urls import path
from . import views

urlpatterns = [
    path('catalog/', views.catalog, name='catalog'),
    path('catalog/courses/<str:department>', views.courses, name='courses'),
    path('about/', views.about, name='about'),
    path('login/', views.login_user, name='login'),
    path('signup/', views.login_user, name='signup'),
    path('account/', views.account, name='account'),
    path('save-note/', views.save_note, name='save_note'),
    path('course-popup/', views.popup, name='popup')
]
