from django.urls import path
# from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # root URL shows login page
    path('dashboard/', views.dashboard, name='dashboard'),#dashboard
    path('signup/', views.signup_view, name='signup'),  #signup
    path('login/', views.login_view, name='login'),#login
    # path('accounts/login/', auth_views.LoginView.as_view(), name='accounts_login'),
    #----------------image--------
    path('image/encrypt/', views.image_encrypt, name='image_encrypt'),
    path('image/decrypt/', views.image_decrypt, name='image_decrypt'),
    path('image_steg/', views.image_steg, name='image_steg'),
   # path('video_steg/', views.video_steg, name='video_steg'),
    #-----------logout---------------
    path('logout/', views.LogoutView.as_view(next_page='login'), name='logout'),
    #------------audio---------------
    path('audio_steg/', views.audio_steg, name='audio_steg'),
    path('audio/encrypt/', views.audio_encrypt, name='audio_encrypt'),
    path('audio/decrypt/', views.audio_decrypt, name='audio_decrypt'),
    #--------video-------------------
    path('video/', views.video_steg, name='video_steg'),
    path('video/encrypt/', views.video_encrypt, name='video_encrypt'),
    path('video/decrypt/', views.video_decrypt, name='video_decrypt'),

]
