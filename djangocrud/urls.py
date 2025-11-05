"""djangocrud URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks import views
from tasks import reports

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'),
    path('tasks/', views.tasks, name='tasks'),
    path('tasks/details/', views.tasks_details, name='tasks_details'),
    path('tasks/details/pdf/', views.tasks_details_pdf, name='tasks_details_pdf'),
    path('tasks_completed/', views.tasks_completed, name='tasks_completed'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('create_task/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>', views.task_detail, name='task_detail'),
    path('taks/<int:task_id>/complete', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete', views.delete_task, name='delete_task'),
    
    # URLs para reportes
    path('reports/', reports.task_reports, name='reports'),
    path('reports/created/', reports.report_tasks_created_period, name='report_tasks_created'),
    path('reports/completed/', reports.report_tasks_completed_period, name='report_tasks_completed'),
    path('reports/by_user/', reports.report_tasks_by_user, name='report_tasks_by_user'),
    path('reports/by_importance/', reports.report_tasks_by_importance, name='report_tasks_by_importance'),
    path('reports/old_pending/', reports.report_old_pending_tasks, name='report_old_pending_tasks'),
    
    # URLs para CAPTCHA
    path('captcha/', include('captcha.urls')),
]
