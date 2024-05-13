from PIL import Image
from django.db import connection
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from secrets import token_hex
from django.utils import timezone
import logging
import jwt
import os
import json
import base64

from user.models import Credentials
from .queries import get_video_list_query, get_video_by_genre_query
from .models import Video, TempVideo, VideoGenre
from core.serializer import VideoSerializer, TempVideoSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_video(request):
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
            except jwt.InvalidTokenError:
                return JsonResponse({'message': 'Invalid token'},
                                    status=status.HTTP_403_FORBIDDEN)
            user = Credentials.objects.filter(username=payload['username'],
                                              email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            with open('directory.json') as f:
                data = json.load(f)
            temp_videos_dir = data['temp_videos_dir']
            thumbnail_dir = data['thumbnail_dir']
            if not os.path.exists(temp_videos_dir):
                os.makedirs(temp_videos_dir)
            serial = token_hex(12)  
            video_file = request.FILES['video']
            video_path = os.path.join(temp_videos_dir,
                                      f'{serial}.{video_file.name.split(".")[-1]}')
            with open(video_path, 'wb') as f:
                for chunk in video_file.chunks():
                    f.write(chunk)
            image_added = False
            try:
                thumbnail_file = request.FILES.get('thumbnail')
                if thumbnail_file and thumbnail_file != 'undefined':
                    thumbnail_path = os.path.join(thumbnail_dir, f'{serial}.jpg')
                    with open(thumbnail_path, 'wb') as f:
                        for chunk in thumbnail_file.chunks():
                            f.write(chunk)
                    image_added = True
                    if thumbnail_file.name.split(".")[-1].lower() != "jpg":
                        try:
                            image = Image.open(thumbnail_path)
                            if image.mode != 'RGB':
                                image = image.convert('RGB')
                            image.save(thumbnail_path, format='JPEG', quality=95)
                        except Exception as e:
                            error_message = f"Error converting thumbnail image to JPG: {str(e)}"
                            logging.error(error_message)
                            return JsonResponse({'message': error_message},
                                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                error_message = f"Error handling thumbnail file: {str(e)}"
                logging.error(error_message)
                return JsonResponse({'message': error_message},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            privatedata = True
            if request.data.get('private') == 'false':
                privatedata = False
            else:
                privatedata = True
            tags = request.data.get('tags', '[]')
            writers = request.data.get('writers', '[]')
            directors = request.data.get('directors', '[]')
            stars = request.data.get('stars', '[]')
            creators = request.data.get('creators', '[]')
            video = TempVideo.objects.create(
                video_name=video_file.name.split('.')[0],
                current_status='File Uploaded',
                last_updated=timezone.now(),
                description=request.data.get('description', ''),
                uploaded_by=user,
                tags=tags,
                serial=serial,
                private=privatedata,
                upload_success=True,
                image_added=image_added,
                imdb_link=request.data.get('imdbLink', ''),
                writers=writers,
                creators=creators,
                directors=directors,
                stars=stars,
                title=request.data.get('title', ''),
                uploaded_date=timezone.now(),
                video_location=temp_videos_dir,
            )
            serializer = TempVideoSerializer(video)
            return JsonResponse({'message': "Video Uploaded \nYou can check the processing status of your video in the 'My Videos' section"},
                                status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        error_message = f"Error during video upload: {str(e)}"
        logging.error(error_message)
        return JsonResponse({'message': error_message},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_videos(request):
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
            user_id = user.id
            viewer_permission_level = user.permission
            with open('directory.json', 'r') as f:
                directory = json.load(f)
            query = get_video_list_query(user_id, viewer_permission_level)
            directory_path =  ''#directory['thumbnail_dir']
            with connection.cursor() as cursor:
                cursor.execute(query, [directory_path, user_id, viewer_permission_level])
                columns = [col[0] for col in cursor.description]
                videos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for video in videos:
                thumbnail_location = video.get('thumbnail_location')
                if thumbnail_location:
                    serial = video['serial']
                    image_path = f"data/thumbnails/{serial}.jpg"
                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                            video['image_url'] = f"data:image/jpeg;base64,{encoded_image}"
                    except FileNotFoundError:
                        logging.error(f"Image file not found: {image_path}")
                    except Exception as e:
                        logging.error(f"Error during image encoding: {str(e)}")
            return JsonResponse({'videos': videos}, status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def video_data(request, serial):
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
            user = Credentials.objects.filter(
                username=payload['username'], email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_data = Video.objects.filter(serial=serial).first()
            if not video_data:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND) 
            length = video_data.visual_profile.get('duration', 0)   
            video = {
                'video_name': video_data.title,
                'video_directors': video_data.directors,
                'video_stars': video_data.stars,
                'video_writers': video_data.writers,
                'video_creators': video_data.creators,
                'video_genre': video_data.tags,
                'video_duration': length,
                'video_description': video_data.description,
                'video_rating': video_data.imdb_rating,
            }
            return JsonResponse(video,
                                status=status.HTTP_200_OK)   
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_genres(request):
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
            genres_queryset = VideoGenre.objects.filter(
                number_of_public_records__gte=1).values('genre')
            genres_list = list(genres_queryset)
            print(genres_list)
            return JsonResponse({'genres': genres_list},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_by_genre(request, genre):
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
            with connection.cursor() as cursor:
                cursor.execute(get_video_by_genre_query(),
                               [user.permission, user.permission, genre])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = [dict(zip(columns, row)) for row in rows]
            for video in videos:
                thumbnail_location = video['thumbnail_location']
                thumbnail_location = thumbnail_location.rstrip('/')
                image_path = f"{thumbnail_location}/{video['serial']}.jpg"
                try:
                    with open(image_path, 'rb') as image_file:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        video['image_url'] = f"data:image/jpeg;base64,{encoded_image}"
                except FileNotFoundError:
                    logging.error(f"Image file not found: {image_path}")
                    video['image_url'] = ''
                except Exception as e:
                    logging.error(f"Error during image encoding: {str(e)}")
                    video['image_url'] = ''
            return JsonResponse({'videos': videos},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['PATCH'])
def TEMPLATE(request):
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
            user = Credentials.objects.filter(username=payload['username'], email=payload['email']).first()
            if not user:
                return JsonResponse({'message': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)