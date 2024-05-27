from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from secrets import token_hex
from PIL import Image

import base64
import logging
import hashlib
import json
import jwt
import os

from user.models import Credentials
from videos.models import Video
from core.serializer import VideoSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
def import_identifier_api(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            data = data['data']
            with open('directory.json', 'r') as f:
                directory = json.load(f)                
            temp_file = token_hex(8)
            with open(f'{directory["temp_json_dir"]}/{temp_file}.json', 'w') as f:
                json.dump(data, f)
            return JsonResponse({'success': 'Data imported'},
                                status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(e)
        return JsonResponse({'error': 'An error occurred'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_my_videos(request):
    try:
        if request.method == 'GET':
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
            videos = Video.objects.filter(uploaded_by_id=user.id).all()[:5]
            all_videos = []
            for video in videos:
                all_videos.append({
                    'title': video.title,
                    'description': video.description,
                    'uploaded_date': video.uploaded_date,
                    'serial': video.serial,
                })
            return JsonResponse({'videos': all_videos},
                                status=status.HTTP_200_OK)   
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_my_uploads(request, page):
    try:
        if request.method == 'GET':
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
            page = int(page)
            page_size = 5
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            
            videos = Video.objects.filter(uploaded_by_id=user.id)[start_index:end_index]
            all_videos = []
            for video in videos:
                all_videos.append({
                    'title': video.title,
                    'description': video.description,
                    'uploaded_date': video.uploaded_date,
                    'serial': video.serial,
                })
            return JsonResponse({'videos': all_videos},
                                status=status.HTTP_200_OK)   
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_record(request, serial):
    try:
        if request.method == 'GET':
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
            video_record = Video.objects.filter(serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            image_pathway = video_record.thumbnail_location + video_record.serial + '.jpg'
            image = base64.b64encode(open(image_pathway, 'rb').read()).decode('utf-8')        
            data = {
                'title': video_record.title,
                'description': video_record.description,
                'uploaded_date': video_record.uploaded_date,
                'serial': video_record.serial,
                'private': video_record.private,
                'genres': video_record.tags,
                'imdb_link': video_record.imdb_link,
                'directors': video_record.directors,
                'stars': video_record.stars,
                'writers': video_record.writers,
                'creators': video_record.creators,
                'current_status': video_record.current_status,
                'image': f'data:image/jpg;base64,{image}',
            }
            return JsonResponse({'video': data},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def update_video_record(request, serial):
    try:
        if request.method == 'PATCH':
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
            video_record = Video.objects.filter(serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            if 'image' in request.FILES:
                image_file = request.FILES['image']
                image_extension = os.path.splitext(
                    image_file.name)[1].lower()
                if image_extension in [
                    '.jpg', '.jpeg', '.png','.gif',
                    '.bmp', '.tiff', '.webp', 'img'
                    ]:
                    os.remove(f'{video_record.thumbnail_location}{serial}.jpg')
                    with Image.open(image_file) as img:
                        img = img.convert("RGB")
                        img = img.resize((190, 281), Image.ANTIALIAS)
                        image_path = os.path.join(directory['thumbnail_dir'],
                                                  f'{serial}.jpg')
                        img.save(image_path, format='JPEG')
                        video_record.thumbnail_location = directory['thumbnail_dir']
                        video_record.image = image_path
                else:
                    return JsonResponse({'message': 'Unsupported image format'},
                                        status=status.HTTP_400_BAD_REQUEST)
            data = request.data
            video_record.title = data['title']
            video_record.description = data['description']
            video_record.tags = data['genres']
            video_record.imdb_link = data['imdb_link']
            video_record.directors = data['directors']
            video_record.stars = data['stars']
            video_record.writers = data['writers']
            video_record.creators = data['creators']
            video_record.private = data['private']
            video_record.save()
            return JsonResponse({'message': 'Video record updated successfully'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_video_record(request, serial):
    try:
        if request.method == 'DELETE':
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
            video_record = Video.objects.filter(serial=serial).first()  
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            os.remove(f'{video_record.thumbnail_location}{serial}.jpg')
            os.remove(f'{video_record.video_location}{serial}.mp4')
            video_record.delete()
            return JsonResponse({'message': 'Video deleted'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PATCH'])
def change_password(request):
    try:
        if request.method == 'PATCH':
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
            data = request.data
            if hashlib.sha256(data['old_password'].encode()).hexdigest() != user.password:
                return JsonResponse({'message': 'Incorrect old password'},
                                    status=status.HTTP_400_BAD_REQUEST)
            user.password = hashlib.sha256(data['new_password'].encode()).hexdigest()
            user.save()
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)