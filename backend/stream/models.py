from django.db import models

class VideoTimestamp(models.Model):
    serial = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='watch_location', default=None)
    time_stamp = models.CharField(max_length=100, default="")
    user = models.ForeignKey('user.Credentials', on_delete=models.CASCADE, related_name='watch_location', default=None)
    
    class Meta:
        db_table = 'video_timestamp'
        verbose_name = 'Video Timestamp'
        verbose_name_plural = 'Video Timestamps'