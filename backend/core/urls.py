"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path
import videos.views as videos_views
import user.views as user_views
import stream.views as stream_views
import management.views as management_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    #auth paths
    path('register/', user_views.register, name='register'),
    path('verification/', user_views.verification, name='verification'),
    path('login/', user_views.login, name='login'),
    path('logout/', user_views.logout, name='logout'),
    
    #video upload and get paths
    path('upload/', videos_views.upload_video, name='upload_video'),
    path('get_videos/', videos_views.get_videos, name='get_videos'),
    path('video_data/<str:serial>/', videos_views.video_data, name='video_data'),
    path('get_genres/', videos_views.get_genres, name='get_genres'),
    path('get_video_by_genre/<str:genre>/', videos_views.get_video_by_genre, name='get_video_by_genre'),
    
    #streaming paths
    path('stream/<str:serial>/<str:permission>/', stream_views.video_stream, name='video_stream'),
    
    #management paths
    path('import_identifier/', management_views.import_identifier_api, name='import_identifier'),
    
    #user paths
]
