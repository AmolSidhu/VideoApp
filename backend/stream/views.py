from django.http import JsonResponse, StreamingHttpResponse, FileResponse
from django.core.files import File
from rest_framework import status
from rest_framework.decorators import api_view
import logging
import jwt
import os
import re
import mimetypes
from io import BytesIO
from wsgiref.util import FileWrapper

from user.models import Credentials
from videos.models import Video

logger = logging.getLogger(__name__)



@api_view(['GET'])
def video_stream(request, serial, permission):
    try:
        if request.method == 'GET':
            token = permission
            if not token:
                return JsonResponse({'message': 'Invalid or missing token'}, status=status.HTTP_403_FORBIDDEN)

            try:
                payload = jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'Token expired'}, status=status.HTTP_403_FORBIDDEN)

            user = Credentials.objects.filter(username=payload['username'], email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

            video = Video.objects.filter(serial=serial).first()
            if not video:
                return JsonResponse({'message': 'Video not found'}, status=status.HTTP_404_NOT_FOUND)

            video_path = os.path.join(video.video_location, f'{video.serial}.mp4')
            
            if not os.path.exists(video_path):
                return JsonResponse({'message': 'Video file not found'}, status=status.HTTP_404_NOT_FOUND)

            range_header = request.META.get('HTTP_RANGE', '').strip()
            range_match = re.match(r'bytes=(\d+)-(\d+)?', range_header)
            size = os.path.getsize(video_path)
            content_type, encoding = mimetypes.guess_type(video_path)

            if range_match:
                first_byte, last_byte = range_match.groups()
                first_byte = int(first_byte) if first_byte else 0
                last_byte = int(last_byte) if last_byte else size - 1
                last_byte = min(last_byte, size - 1)
                length = last_byte - first_byte + 1
                with open(video_path, 'rb') as f:
                    f.seek(first_byte)
                    data = f.read(last_byte - first_byte + 1)
                resp = StreamingHttpResponse(FileWrapper(BytesIO(data)), status=206, content_type=content_type)
                resp['Content-Length'] = str(length)
                resp['Content-Range'] = f'bytes {first_byte}-{last_byte}/{size}'
            else:
                resp = FileResponse(open(video_path, 'rb'), content_type=content_type)
                resp['Content-Length'] = str(size)
            
            resp['Accept-Ranges'] = 'bytes'
            return resp

    except Exception as e:
        logging.error(f"Error during video streaming: {str(e)}")
        return JsonResponse({'message': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
