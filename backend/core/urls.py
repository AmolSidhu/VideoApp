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
    path('recently_viewed/', videos_views.recently_viewed, name='recently_viewed'),
    
    #streaming paths
    path('stream/<str:serial>/<str:permission>/', stream_views.video_stream, name='video_stream'),
    path('log_video_time/', stream_views.log_video_time, name='log_video_time'),
    path('video_history/<str:serial>/', stream_views.video_history, name='video_history'),
    path('update_playback_time/', stream_views.update_playback_time, name='update_playback_time'),
    
    #management paths
    path('import_identifier/', management_views.import_identifier_api, name='import_identifier'),
    path('get_my_videos/', management_views.get_my_videos, name='get_my_videos'),
    path('get_my_uploads/<int:page>/', management_views.get_my_uploads, name='get_my_uploads'),
    path('get_video_record/<str:serial>/', management_views.get_video_record, name='get_video_record'),
    path('update_video_record/<str:serial>/', management_views.update_video_record, name='update_video_record'),
    path('delete_video_record/<str:serial>/', management_views.delete_video_record, name='delete_video_record'),
    
    #user paths
]
