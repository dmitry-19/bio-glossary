from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from glossary import views


def simple_page(template_name):
    return lambda request: render(request, template_name)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('add-term/', views.add_term, name='add_term'),
    path('terms/', views.term_list, name='term_list'),
    path('statistics/', views.statistics, name='statistics'),
    path('test/', views.test, name='test'),
    path('submit-test/', views.submit_test, name='submit_test'),
    path('success/', simple_page('glossary/success.html'), name='success'),
    path('error/', simple_page('glossary/error.html'), name='error'),
]