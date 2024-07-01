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
    path('upload/batch/', videos_views.upload_batch_videos, name='upload_batch_videos'),
    path('get_videos/', videos_views.get_videos, name='get_videos'),
    path('video_data/<str:serial>/', videos_views.video_data, name='video_data'),
    path('episode_data/<str:serial>/<str:season>', videos_views.episode_data, name='episode_data'),
    path('get_genres/', videos_views.get_genres, name='get_genres'),
    path('get_video_by_genre/<str:genre>/', videos_views.get_video_by_genre, name='get_video_by_genre'),
    path('recently_viewed/', videos_views.recently_viewed, name='recently_viewed'),
    path('video/search/<str:query>/', videos_views.get_video_search, name='get_video_search'),
    
    #streaming paths
    path('stream/<str:serial>/<str:permission>/<str:serial_code>/', stream_views.video_stream, name='video_stream'),
    path('log_video_time/', stream_views.log_video_time, name='log_video_time'),
    path('video_history/<str:serial>/<str:video_type>/', stream_views.video_history, name='video_history'),
    path('update_playback_time/<str:video_type>/<str:serial>/', stream_views.update_playback_time, name='update_playback_time'),
    
    #management paths
    path('import_identifier/', management_views.import_identifier_api, name='import_identifier'),
    path('get_my_videos/', management_views.get_my_videos, name='get_my_videos'),
    path('get_my_uploads/<int:page>/', management_views.get_my_uploads, name='get_my_uploads'),
    path('get_video_record/<str:serial>/', management_views.get_video_record, name='get_video_record'),
    path('update_video_record/<str:serial>/', management_views.update_video_record, name='update_video_record'),
    path('delete_video_record/<str:serial>/', management_views.delete_video_record, name='delete_video_record'),
    path('change_my_password/', management_views.change_password, name='change_password'),
    path('change_my_email/', management_views.change_email, name='change_email'),
    path('change_my_username/', management_views.change_username, name='change_username'),
    path('delete_my_account/', management_views.delete_account, name='delete_account'),
    path('get_season_records/<str:serial>/<str:season>/', management_views.get_season_records, name='get_season_records'),
    path('update_episode_record/<str:serial>/<str:season>/<str:episode>/', management_views.update_episode_record, name='update_episode_record'),
    path('update_season_records/<str:serial>/', management_views.update_season_records, name='update_season_records'),
    path('delete_season_records/<str:serial>/', management_views.delete_season_records, name='delete_season_records'),
    path('delete_episode_record/<str:serial>/<str:season>/<str:episode>/', management_views.delete_episode_record, name='delete_episode_record'),
    
    #user paths
    path('change_password/', user_views.change_password, name='change_password'),
    path('forgot_password/', user_views.forgot_password, name='forgot_password'),
    path('resend_verification/', user_views.resend_verification, name='resend_verification'),
]
