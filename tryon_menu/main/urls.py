from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('upload/', views.upload_images, name='upload_images'),
    path('inputsets/', views.inputset_list, name='inputset_list'),
    path('inputsets/<int:inputset_id>/', views.inputset_detail, name='inputset_detail'),
    path('batch/create/', views.create_tryonbatch_step1, name='create_tryonbatch_step1'),
    path('batch/create/step2/', views.create_tryonbatch_step2, name='create_tryonbatch_step2'),
    path('batch/<int:batch_id>/', views.tryonbatch_detail, name='tryonbatch_detail'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('reset-password/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
] 