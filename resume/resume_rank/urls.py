from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views


urlpatterns = [ 
    path('', views.index, name='resume_rank'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('recruit/', views.recruit, name='recruit'),
    path('users/', views.user_list, name='users_list'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/add/', views.add_job, name='add_job'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/', views.resume_list, name='resume'),
    path('score/', views.score, name='score'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)