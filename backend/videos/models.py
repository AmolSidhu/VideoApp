from django.db import models

class TempVideo(models.Model):
    video_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="")
    video_location = models.CharField(max_length=300)
    thumbnail_location = models.CharField(max_length=300)
    image_added = models.BooleanField(default=False)
    imdb_link = models.CharField(max_length=300, default="")
    imdb_rating = models.FloatField(default=0)
    imdb_link_failed = models.BooleanField(default=False)
    failed_attempts = models.IntegerField(default=0)
    imdb_failed_attempts = models.IntegerField(default=0)
    main_tag = models.CharField(max_length=100, default="")
    tags = models.JSONField(default=list)
    directors = models.JSONField(default=list)
    stars = models.JSONField(default=list)
    writers = models.JSONField(default=list)
    creators = models.JSONField(default=list)
    permission = models.IntegerField(default=1)
    rating = models.FloatField(default=0)
    series = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='temp_videos', default=None)
    total_rating_score = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    visual_profile = models.JSONField(default=dict)
    audio_profile = models.JSONField(default=dict)
    visual_details = models.JSONField(default=dict)
    audio_details = models.JSONField(default=dict)
    current_status = models.CharField(max_length=100, default="Failed to Upload")
    uploaded_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(default="")
    genre_updated = models.BooleanField(default=True)
    serial = models.CharField(max_length=100, unique=True)
    master_serial = models.CharField(max_length=100, null=True)
    season = models.IntegerField(default=0)
    episode = models.IntegerField(default=0)
    existing_series = models.BooleanField(default=False)
    corruption_check_temp = models.BooleanField(default=False)
    format_conversion = models.BooleanField(default=False)
    corruption_check_data = models.BooleanField(default=False)
    imdb_added = models.BooleanField(default=False)
    image_added = models.BooleanField(default=False)
    visual_data_added = models.BooleanField(default=False)
    audio_data_added = models.BooleanField(default=False)
    upload_success = models.BooleanField(default=True)
    temp_video_location = models.CharField(max_length=300, default="")
    
    def __str__(self):
        return self.video_name + " - " + str(self.rating)
    
    class Meta:
        db_table = 'temp_video'
        verbose_name = 'Temp Video'
        verbose_name_plural = 'Temp Videos'

class NonSeriesVideo(models.Model):
    video_instance = models.ForeignKey('videos.video', on_delete=models.CASCADE, related_name='non_series_videos')
    video_serial = models.CharField(max_length=100)
    video_name = models.CharField(max_length=100)
    video_location = models.CharField(max_length=300)
    thumbnail_location = models.CharField(max_length=300)
    visual_profile = models.JSONField(default=dict)
    audio_profile = models.JSONField(default=dict)
    visual_details = models.JSONField(default=dict)
    audio_details = models.JSONField(default=dict)
    current_status = models.CharField(max_length=100, default="Failed to Upload")
    
    def __str__(self):
        return self.video_name
    
    class Meta:
        db_table = 'non_series_video'
        verbose_name = 'Non Series Video'
        verbose_name_plural = 'Non Series Videos'

class SeriesVideo(models.Model):
    batch_instance = models.ForeignKey('videos.video', on_delete=models.CASCADE, related_name='series_videos')
    video_serial = models.CharField(max_length=100, unique=True)
    season = models.IntegerField(default=0)
    episode = models.IntegerField(default=0)
    video_name = models.CharField(max_length=100)
    video_location = models.CharField(max_length=300)
    thumbnail_location = models.CharField(max_length=300)
    visual_profile = models.JSONField(default=dict)
    audio_profile = models.JSONField(default=dict)
    visual_details = models.JSONField(default=dict)
    audio_details = models.JSONField(default=dict)
    current_status = models.CharField(max_length=100, default="Failed to Upload")
    
    def __str__(self):
        return self.video_name
    
    class Meta:
        db_table = 'series_video'
        verbose_name = 'Series Video'
        verbose_name_plural = 'Series Videos'
        
class Video(models.Model):
    serial = models.CharField(max_length=100)
    series = models.BooleanField(default=False)
    total_seasons = models.IntegerField(default=0)
    total_episodes = models.IntegerField(default=0)
    title = models.CharField(max_length=100, default="")
    season_metadata = models.JSONField(default=dict)
    imdb_link = models.CharField(max_length=300, default="")
    imdb_rating = models.FloatField(default=0)
    main_tag = models.CharField(max_length=100, default="")
    tags = models.JSONField(default=list)
    directors = models.JSONField(default=list)
    stars = models.JSONField(default=list)
    writers = models.JSONField(default=list)
    creators = models.JSONField(default=list)
    permission = models.IntegerField(default=1)
    rating = models.FloatField(default=0)
    private = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='videos', default=None)
    total_rating_score = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(default="")
    genre_updated = models.BooleanField(default=True)
    update_series = models.BooleanField(default=False)
    current_status = models.CharField(max_length=100, default="Failed to Upload")
    
    def __str__(self):
        return self.title + " - " + str(self.uploaded_by)
    
    class Meta:
        db_table = 'video'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'

class VideoComments(models.Model):
    video_serial = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.video_serial + " - " + self.user + " - " + self.comment[:10]
    
    class Meta:
        db_table = 'video_comments'
        verbose_name = 'Video Comment'
        verbose_name_plural = 'Video Comments'
    
class VideoHistory(models.Model):
    video_serial = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='history')
    serial = models.CharField(max_length=100)
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='history')
    video_stop_time = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.video_serial + " - " + self.user + " - " + str(self.timestamp)
    
    class Meta:
        db_table = 'video_history'
        verbose_name = 'Video History'
        verbose_name_plural = 'Video Histories'

class VideoGenre(models.Model):
    genre = models.CharField(max_length=100, unique=True)
    number_of_public_records = models.IntegerField(default=0)
    custom = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'video_genre'
        verbose_name = 'Video Genre'
        verbose_name_plural = 'Video Genres'
