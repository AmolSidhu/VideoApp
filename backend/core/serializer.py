from rest_framework import serializers
from videos.models import Video, TempVideo, VideoGenre, SeriesVideo, NonSeriesVideo
from user.models import Credentials
from management.models import Identifier

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        
class TempVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempVideo
        fields = '__all__'
        
class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credentials
        fields = '__all__'

class IdentifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Identifier
        fields = '__all__'

class VideoGenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoGenre
        fields = '__all__'

class SeriesVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SeriesVideo
        fields = '__all__'

class NonSeriesVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = NonSeriesVideo
        fields = '__all__'