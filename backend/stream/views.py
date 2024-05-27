from django.http import JsonResponse, StreamingHttpResponse, FileResponse
from django.core.files import File
from rest_framework import status
from rest_framework.decorators import api_view
import logging
import jwt
import time
import json
import os
import re
import mimetypes
from io import BytesIO
from wsgiref.util import FileWrapper

from user.models import Credentials
from videos.models import Video, VideoHistory

logger = logging.getLogger(__name__)

@api_view(['GET'])
def video_stream(request, serial, permission):
    try:
        if request.method == 'GET':
            token = permission
            if not token:
                return JsonResponse({'message': 'Invalid or missing token'},
                                    status=status.HTTP_403_FORBIDDEN)
            try:
                payload = jwt.decode(token, 'SECRET_KEY',
                                     algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expired'},
                                    status=status.HTTP_403_FORBIDDEN)
            user = Credentials.objects.filter(username=payload['username'],
                                              email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video = Video.objects.filter(serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_path = os.path.join(video.video_location, f'{video.serial}.mp4')
            if not os.path.exists(video_path):
                return JsonResponse({'message': 'Video file not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            resume = request.GET.get('resume', 'false').lower() == 'true'
            resume_time = 0
            if resume:
                video_history = VideoHistory.objects.filter(user=user, video_serial=video).first()
                if video_history:
                    resume_time = video_history.video_stop_time
            size = os.path.getsize(video_path)
            content_type, _ = mimetypes.guess_type(video_path)
            range_header = request.META.get('HTTP_RANGE', '').strip()
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
            if range_match:
                first_byte, last_byte = range_match.groups()
                first_byte = int(first_byte) if first_byte else 0
                last_byte = int(last_byte) if last_byte else size - 1
                last_byte = min(last_byte, size - 1)
                length = last_byte - first_byte + 1
                with open(video_path, 'rb') as f:
                    f.seek(first_byte)
                    data = f.read(last_byte - first_byte + 1)
                response = StreamingHttpResponse(FileWrapper(BytesIO(data)),
                                                 status=status.HTTP_206_PARTIAL_CONTENT,
                                                 content_type=content_type)
                response['Content-Length'] = str(length)
                response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
            else:
                response = StreamingHttpResponse(FileWrapper(open(video_path, 'rb')),
                                                 content_type=content_type)
                response['Content-Length'] = str(size)
            response['Accept-Ranges'] = 'bytes'
            response['Resume-Time'] = str(resume_time)

            # No need for on_close function here

            # Instead, simply return the response
            return response
    except Exception as e:
        logging.error(f"Error during video streaming: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)





@api_view(['POST'])
def log_video_time(request):
    try:
        if request.method == 'POST':
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'message': 'Invalid or missing token'},
                                    status=status.HTTP_403_FORBIDDEN)
            try:
                payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expired'},
                                    status=status.HTTP_403_FORBIDDEN)
            user = Credentials.objects.filter(username=payload['username'],
                                              email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            serial = request.data.get('serial')
            timestamp = request.data.get('timestamp')
            video = Video.objects.filter(serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            history_record = VideoHistory.objects.filter(
                user=user, video_serial=serial).first()
            if not history_record:
                new_record = VideoHistory.objects.create(
                    user=user, video_serial=serial, video_stop_time=timestamp)
                new_record.save()
            else:
                history_record.video_stop_time = timestamp
                history_record.save()
            return JsonResponse({'message': 'Timestamp logged'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def video_history(request, serial):
    try:
        token = request.headers.get('Authorization')
        if not token:
            return JsonResponse({'message': 'Invalid or missing token'},
                                status=status.HTTP_403_FORBIDDEN)
        try:
            payload = jwt.decode(token, 'SECRET_KEY',
                                 algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'message': 'Token expired'},
                                status=status.HTTP_403_FORBIDDEN)
        user = Credentials.objects.filter(username=payload['username'],
                                          email=payload['email']).first()
        if not user:
            return JsonResponse({'message': 'User not found'},
                                status=status.HTTP_404_NOT_FOUND)
        video = Video.objects.filter(serial=serial).first()
        if not video:
            return JsonResponse({'message': 'Video not found'},
                                status=status.HTTP_404_NOT_FOUND)
        video_history = VideoHistory.objects.filter(user=user,
                                                    video_serial=video).first()
        if not video_history:
            return JsonResponse({'video_stop_time': 0},
                                status=status.HTTP_200_OK)
        return JsonResponse({'video_stop_time': video_history.video_stop_time},
                            status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error fetching video history: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['POST'])
def update_playback_time(request):
    try:
        if request.method == 'POST':
            token = request.headers.get('Authorization')
            if not token:
                return JsonResponse({'message': 'Invalid or missing token'},
                                    status=status.HTTP_403_FORBIDDEN)
            try:
                payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expired'},
                                    status=status.HTTP_403_FORBIDDEN)
            user = Credentials.objects.filter(username=payload['username'],
                                              email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            serial = request.data.get('serial')
            video_stop_time = request.data.get('currentTime')
            video = Video.objects.filter(serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            history = VideoHistory.objects.filter(user=user,
                                                  video_serial=video).first()
            if not history:
                history = VideoHistory.objects.create(user=user,
                                                      video_serial=video,
                                                      video_stop_time=video_stop_time
                                                      )
            else:
                history.video_stop_time = video_stop_time
                history.save()
            return JsonResponse({'message': 'Playback time updated'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)