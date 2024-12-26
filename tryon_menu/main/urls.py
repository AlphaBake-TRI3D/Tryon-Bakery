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
    path('modelversions/', views.modelversion_list, name='modelversion_list'),
    path('modelversions/<int:modelversion_id>/', views.modelversion_detail, name='modelversion_detail'),
    path('rank/', views.batch_selection, name='batch_selection'),
    path('rank/comparison/<int:batch_id>/', views.comparison_view, name='comparison_view'),
    path('rank/submit/', views.submit_ranking, name='submit_ranking'),
    path('my-rankings/', views.my_rankings, name='my_rankings'),
    path('my-rankings/delete/<int:ranking_id>/', views.delete_ranking, name='delete_ranking'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset_view, name='password_reset'),
    path('reset-password/<str:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
] 