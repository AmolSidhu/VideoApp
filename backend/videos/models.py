from django.db import models


class Video(models.Model):
    video_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="")
    video_location = models.CharField(max_length=300, default='data/videos/')
    thumbnail_location = models.CharField(max_length=300, default='data/thumbnails/')
    name = models.CharField(max_length=100, default="")
    main_tag = models.CharField(max_length=100, default="")
    tags = models.JSONField(default=list)
    imdb_link = models.CharField(max_length=300, default="")
    imdb_rating = models.FloatField(default=0)
    serial = models.CharField(max_length=100, unique=True)
    directors = models.JSONField(default=list)
    stars = models.JSONField(default=list)
    writers = models.JSONField(default=list)
    creators = models.JSONField(default=list)
    permission = models.IntegerField(default=1)
    rating = models.FloatField(default=0)
    series = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='videos', default=None)
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
    
    def __str__(self):
        return self.video_name + " - " + str(self.rating)
    
    class Meta:
        db_table = 'video'
        verbose_name = 'Video'
        verbose_name_plural = 'Videos'
    
    
class TempVideo(models.Model):
    video_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, default="")
    video_location = models.CharField(max_length=300, default="temp_videos/")
    thumbnail_location = models.CharField(max_length=300, default="data/thumbnails/")
    name = models.CharField(max_length=100, default="")   # delete this
    image_added = models.BooleanField(default=False)
    imdb_link = models.CharField(max_length=300, default="")
    imdb_rating = models.FloatField(default=0)
    imdb_link_failed = models.BooleanField(default=False)
    imdb_failed_attempts = models.IntegerField(default=0)
    main_tag = models.CharField(max_length=100, default="")
    tags = models.JSONField(default=list)
    directors = models.JSONField(default=list)
    stars = models.JSONField(default=list)
    writers = models.JSONField(default=list)
    creators = models.JSONField(default=list)
    serial = models.CharField(max_length=100, unique=True)
    permission = models.IntegerField(default=1)
    series = models.BooleanField(default=False)
    private = models.BooleanField(default=False)
    upload_success = models.BooleanField(default=False)
    corruption_check_temp = models.BooleanField(default=False)
    imdb_added = models.BooleanField(default=False)
    format_conversion = models.BooleanField(default=False)
    corruption_check_data = models.BooleanField(default=False)
    visual_data_added = models.BooleanField(default=False)
    audio_data_added = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='temp_videos', default=None)
    total_rating_score = models.FloatField(default=0)
    total_ratings = models.IntegerField(default=0)
    visual_profile = models.JSONField(default=dict)
    audio_profile = models.JSONField(default=dict)
    visual_details = models.JSONField(default=dict)
    audio_details = models.JSONField(default=dict)
    current_status = models.CharField(max_length=100, default="Failed to Upload")
    failed_attempts = models.IntegerField(default=0)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    description = models.TextField(default="")
    
    def __str__(self):
        return self.video_name + " - " + str(self.rating)
    
    class Meta:
        db_table = 'temp_video'
        verbose_name = 'Temp Video'
        verbose_name_plural = 'Temp Videos'

class VideoComments(models.Model):
    video_serial = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.video.video_name + " - " + self.user.username + " - " + self.comment[:10]
    
    class Meta:
        db_table = 'video_comments'
        verbose_name = 'Video Comment'
        verbose_name_plural = 'Video Comments'
    
class VideoHistory(models.Model):
    video_serial = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='history')
    video_stop_time = models.FloatField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.video.video_name + " - " + self.user.username + " - " + str(self.timestamp)
    
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
    