from PIL import Image
from django.db import connection
from django.http import JsonResponse, HttpRequest
from rest_framework import status
from rest_framework.decorators import api_view
from secrets import token_hex
from django.utils import timezone
import logging
import jwt
import os
import json
import base64

from functions.function import auth_check
from user.models import Credentials
from .queries import get_video_list_query, get_video_by_genre_query, get_recently_viewed_query, get_video_search_query
from .models import Video, TempVideo, VideoGenre, VideoHistory, NonSeriesVideo, SeriesVideo
from core.serializer import VideoSerializer, TempVideoSerializer

logger = logging.getLogger(__name__)

@api_view(['POST'])
def upload_video(request):
    try:
        if request.method == 'POST':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            with open('directory.json') as f:
                data = json.load(f)
            temp_videos_dir = data['temp_videos_dir']
            thumbnail_dir = data['thumbnail_dir']
            video_dir = data['video_dir']
            os.makedirs(temp_videos_dir, exist_ok=True)
            os.makedirs(thumbnail_dir, exist_ok=True)
            os.makedirs(video_dir, exist_ok=True)
            serial = token_hex(12)
            master_serial = token_hex(12)  
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
            tags = json.loads(request.data.get('tags', '[]'))
            writers = json.loads(request.data.get('writers', '[]'))
            directors = json.loads(request.data.get('directors', '[]'))
            stars = json.loads(request.data.get('stars', '[]'))
            creators = json.loads(request.data.get('creators', '[]'))
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
                temp_video_location=temp_videos_dir,
                thumbnail_location=thumbnail_dir,
                permission=request.data.get('permission', 1),
                series=False,
                uploaded_by_id=user.id,
                master_serial=master_serial,
                season=0,
                episode=0,
                existing_series=False,
                video_location=video_dir
            )
            serializer = TempVideoSerializer(video)
            return JsonResponse({'message': "Video Uploaded \nYou can check the processing status of your video in the 'My Videos' section"},
                                status=status.HTTP_202_ACCEPTED)
    except Exception as e:
        error_message = f"Error during video upload: {str(e)}"
        logging.error(error_message)
        return JsonResponse({'message': error_message},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def upload_batch_videos(request):
    try:
        if request.method == 'PATCH':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            with open('directory.json') as f:
                data = json.load(f)
            temp_videos_dir = data['temp_videos_dir']
            thumbnail_dir = data['thumbnail_dir']
            video_dir = data['video_dir']
            os.makedirs(temp_videos_dir, exist_ok=True)
            os.makedirs(thumbnail_dir, exist_ok=True)
            os.makedirs(video_dir, exist_ok=True)
            videos = request.FILES.getlist('videos')
            thumbnail_file = request.FILES.get('thumbnail')
            if request.data.get('existing_series') == 'true':
                record = Video.objects.filter(title=request.data.get('title', '')).first()
                if not record:
                    record = TempVideo.objects.filter(title=request.data.get('title', '')).first()
                    if not record:
                        record = Video.objects.filter(imdb_link=request.data.get('imdbLink', '')).first()
                        if not record:
                            record = TempVideo.objects.filter(imdb_link=request.data.get('imdbLink', '')).first()
                master_serial = record.id
            else:
                master_serial = token_hex(12)
            thumbnail_path = None
            image_added = False
            if thumbnail_file:
                thumbnail_ext = thumbnail_file.name.split(".")[-1]
                thumbnail_path = os.path.join(thumbnail_dir, f'{master_serial}.jpg')
                with open(thumbnail_path, 'wb') as f:
                    for chunk in thumbnail_file.chunks():
                        f.write(chunk)
                image_added = True
                if thumbnail_ext.lower() != "jpg":
                    try:
                        image = Image.open(thumbnail_path)
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        image.save(thumbnail_path, format='JPEG', quality=95)
                    except Exception as e:
                        error_message = f"Error converting thumbnail image to JPG: {str(e)}"
                        return JsonResponse({'message': error_message},
                                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            privatedata = False
            if request.data.get('private') == 'true':
                privatedata = True
            existing_series = False
            if request.data.get('existing_series') == 'true':
                existing_series = True        
            tags = json.loads(request.data.get('tags', '[]'))
            writers = json.loads(request.data.get('writers', '[]'))
            directors = json.loads(request.data.get('directors', '[]'))
            stars = json.loads(request.data.get('stars', '[]'))
            creators = json.loads(request.data.get('creators', '[]'))
            responses = []    
            for i, video_file in enumerate(videos):
                try:
                    serial = token_hex(12)
                    video_ext = video_file.name.split(".")[-1]
                    video_path = os.path.join(temp_videos_dir, f'{serial}.{video_ext}')
                    with open(video_path, 'wb') as f:
                        for chunk in video_file.chunks():
                            f.write(chunk)   
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
                        temp_video_location=temp_videos_dir,
                        thumbnail_location=thumbnail_dir,
                        permission=request.data.get('permission', 1),
                        series=True,
                        uploaded_by_id=user.id,
                        master_serial=master_serial,
                        season=request.data.get('season', 1),
                        episode=i + 1,
                        existing_series=existing_series,
                        video_location=video_dir
                    )
                    responses.append({'video_name': video_file.name, 'message': 'Video Uploaded', 'status': 'success'})
                except Exception as e:
                    logger.error(f"Error during batch video upload: {str(e)}")
                    responses.append({'video_name': video_file.name,
                                    'message': error_message, 'status': 'failed'})
            return JsonResponse({'responses': responses}, status=status.HTTP_207_MULTI_STATUS)
    except Exception as e:
        logger.error(f"Error during batch video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
def get_videos(request):
    try:
        if request.method == 'GET':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            user_id = user.id
            viewer_permission_level = user.permission
            with connection.cursor() as cursor:
                cursor.execute(get_video_list_query(), [user_id, viewer_permission_level])
                columns = [col[0] for col in cursor.description]
                videos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for video in videos:
                thumbnail_location = video['thumbnail_location']
                image_path = r"{}{}.jpg".format(thumbnail_location, video['serial'])
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_data = Video.objects.filter(serial=serial,
                                              uploaded_by_id=user.id).first()
            resume = False
            if video_data.series:
                video_history = VideoHistory.objects.filter(video_serial_id=video_data.id,
                                                            user_id=user.id).first()
                if video_history:
                    resume = True
            if not video_data.series:
                video_history = VideoHistory.objects.filter(video_serial_id=video_data.id,
                                                            user_id=user.id).first()
                if video_history:
                    resume = True
            if not video_data:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video = {
                'video_name': video_data.title,
                'video_directors': video_data.directors,
                'video_stars': video_data.stars,
                'video_writers': video_data.writers,
                'video_creators': video_data.creators,
                'video_genres': video_data.tags,
                'video_description': video_data.description,
                'video_rating': video_data.imdb_rating,
                'resume': resume,
                'resume_serial': video_history.serial if resume else '',
                'series': video_data.series,
            }
            if video_data.series:
                video['season_metadata'] = video_data.season_metadata
            return JsonResponse(video,
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video data retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def episode_data(request, serial, season):
    try:
        if request.method == 'GET':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video = Video.objects.filter(serial=serial, uploaded_by_id=user.id).first()
            if not video:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            season_data = SeriesVideo.objects.filter(batch_instance_id=video.id,
                                                     season=season).values(
                                                         'episode',
                                                         'video_name',
                                                         'video_serial').order_by(
                                                             'episode')
            for episode in season_data:
                history_instance = VideoHistory.objects.filter(
                    serial=episode['video_serial'], user_id=user.id).exists()
                if history_instance:
                    episode['resume'] = True
                else:
                    episode['resume'] = False
            return JsonResponse({'episodes': list(season_data)},
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            genres_queryset = VideoGenre.objects.filter(
                number_of_public_records__gte=1).values('genre')
            genres_list = list(genres_queryset)
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            user_id = user.id
            viewer_permission_level = user.permission
            sql_query = get_video_by_genre_query()
            with connection.cursor() as cursor:
                cursor.execute(sql_query,
                               [user_id, viewer_permission_level, genre])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = [dict(zip(columns, row)) for row in rows]
            for video in videos:
                thumbnail_location = video['thumbnail_location']
                if thumbnail_location:
                    serial = video['serial']
                    image_path = f"{thumbnail_location}/{serial}.jpg"
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
                else:
                    video['image_url'] = ''
            return JsonResponse({'videos': videos},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def recently_viewed(request):
    try:
        if request.method == 'GET':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            user_id = user.id
            viewer_permission_level = user.permission
            query = get_recently_viewed_query()
            with connection.cursor() as cursor:
                cursor.execute(query, [user_id, user_id, viewer_permission_level])
                columns = [col[0] for col in cursor.description]
                rows = cursor.fetchall()
                videos = []
                if rows:
                    videos = [dict(zip(columns, row)) for row in rows]
                    for video in videos:
                        thumbnail_location = video.get('thumbnail_location')
                        if thumbnail_location:
                            serial = video['serial']
                            image_path = f"{thumbnail_location}{serial}.jpg"
                            try:
                                with open(image_path, 'rb') as image_file:
                                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                                    video['image_url'] = f"data:image/jpeg;base64,{encoded_image}"
                            except FileNotFoundError:
                                logging.error(f"Image file not found: {image_path}")
                                video['image_url'] = ''
                return JsonResponse({'videos': videos}, status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_video_search(request, query):
    try:
        if request.method == 'GET':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            user_id = user.id
            viewer_permission_level = user.permission
            sql_query = get_video_search_query()
            with connection.cursor() as cursor:
                cursor.execute(sql_query, [
                    user_id,
                    f"%{query}%",
                    f"%{query}%",
                    viewer_permission_level
                ])
                columns = [col[0] for col in cursor.descrition]
                videos = [dict(zip(columns, row)) for row in cursor.fetchall()]
            for video in videos:
                thumbnail_location = video.get('thumbnail_location')
                if thumbnail_location:
                    serial = video['serial']
                    image_path = f"{thumbnail_location}{serial}.jpg"
                    try:
                        with open(image_path, 'rb') as image_file:
                            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                            video['image_url'] = f"data:image/jpeg;base64,{encoded_image}"
                    except FileNotFoundError:
                        logging.error(f"Image file not found: {image_path}")
                    except Exception as e:
                        logging.error(f"Error during image encoding: {str(e)}")
            return JsonResponse({'videos': videos},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video retrieval: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
