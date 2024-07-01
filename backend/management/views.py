from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from datetime import datetime
from secrets import token_hex
from PIL import Image

import base64
import logging
import hashlib
import json
import jwt
import os

from functions.function import auth_check
from user.models import Credentials
from videos.models import Video, VideoComments, VideoHistory, SeriesVideo, NonSeriesVideo
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            videos = Video.objects.filter(uploaded_by_id=user.id).all().order_by('-last_updated')[:5]
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_record = Video.objects.filter(serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            if video_record.series:
                secondary_record = SeriesVideo.objects.filter(batch_instance=video_record.id).first()
            if not video_record.series:
                secondary_record = NonSeriesVideo.objects.filter(video_instance=video_record.id).first()
            image_pathway = secondary_record.thumbnail_location + video_record.serial + '.jpg'
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
                'season_metadata': video_record.season_metadata,
                'series': video_record.series,
            }
            return JsonResponse({'video': data},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['GET'])
def get_season_records(request, serial, season):
    try:
        if request.method == 'GET':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            master_record = Video.objects.filter(serial=serial, uploaded_by=user.id).first()
            if not master_record:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_records = SeriesVideo.objects.filter(batch_instance=master_record.id,
                                                       season=season).all().order_by('episode')
            video_data = []
            for video_record in video_records:
                video_data.append({
                    'season': video_record.season,
                    'episode': video_record.episode,
                    'episode_serial': video_record.video_serial,
                })
            return JsonResponse({'season': video_data},
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
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
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

@api_view(['PATCH'])
def update_episode_record(request, serial, season, episode):
    try:
        if request.method == 'PATCH':
            print('request data', request.data)
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            master_serial = request.data['master_serial']
            video_record = Video.objects.filter(serial=master_serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            video_serial = request.data['episode_serial']
            episode_record = SeriesVideo.objects.filter(batch_instance=video_record.id,
                                                        episode=episode,
                                                        season=season,
                                                        video_serial=video_serial).first()
            if not episode_record:
                return JsonResponse({'message': 'Episode not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            data = request.data
            episode_record.episode = data['new_episode']
            episode_record.season = data['new_season']
            episode_record.save()
            video_record.update_series = False
            video_record.save()
            return JsonResponse({'message': 'Episode record updated successfully'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['PATCH'])
def update_season_records(request, serial):
    try:
        if request.method == 'PATCH':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            master_id = request.data['master_id']
            season = request.data['season']
            video_record = Video.objects.filter(id=master_id,
                                                serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            season_records = SeriesVideo.objects.filter(batch_instance=master_id,
                                                       season=season).all()
            if not season_records:
                return JsonResponse({'message': 'Season not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            data = request.data
            for season_record in season_records:
                season_record.season = data['new_season']
                season_record.episode = data['new_episode']
                season_record.save()
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_video_record(request, serial):
    try:
        if request.method == 'DELETE':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
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

@api_view(['DELETE'])
def delete_episode_record(request, serial, episode, season):
    try:
        if request.method == 'DELETE':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            video_serial = request.data['episode_serial']
            video_record = Video.objects.filter(serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            episode_record = SeriesVideo.objects.filter(batch_instance=video_record.id,
                                                        episode=episode,
                                                        season=season,
                                                        video_serial=video_serial).first()
            if not episode_record:
                return JsonResponse({'message': 'Episode not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            os.remove(f'{episode_record.video_location}{video_serial}.mp4')
            episode_record.delete()
            video_record.update_series = False
            video_record.save()
            return JsonResponse({'message': 'Episode deleted'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['DELETE'])
def delete_season_records(request, serial):
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
            master_id = request.data['master_id']
            season = request.data['season']
            video_record = Video.objects.filter(id=master_id,
                                                serial=serial).first()
            if not video_record or video_record.uploaded_by_id != user.id:
                return JsonResponse({'message': 'Video not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            season_records = SeriesVideo.objects.filter(batch_instance=master_id,
                                                       season=season).all()
            if not season_records:
                return JsonResponse({'message': 'Season not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            for season_record in season_records:
                os.remove(f'{season_record.video_location}{serial}.mp4')
                season_record.delete()
            return JsonResponse({'message': 'Season deleted'},
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

@api_view(['PATCH'])
def change_email(request):
    try:
        if request.method == 'PATCH':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            data = request.data
            new_email = data['new_email']
            valid_email = Credentials.objects.filter(email=new_email).first()
            if valid_email:
                return JsonResponse({'message': 'Email already in use'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                user.email = new_email
                user.save()
            return JsonResponse({'message': 'Email changed successfully'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
@api_view(['PATCH'])
def change_username(request):
    try:
        if request.method == 'PATCH':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            data = request.data
            new_username = data['new_username']
            valid_username = Credentials.objects.filter(username=new_username).first()
            if valid_username:
                return JsonResponse({'message': 'Username already in use'},
                                    status=status.HTTP_400_BAD_REQUEST)
            else:
                user.username = new_username
                user.save()
        return JsonResponse({'message': 'Username changed successfully'},
                            status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def delete_account(request):
    try:
        if request.method == 'PATCH':
            token = request.headers.get('Authorization')
            auth = auth_check(token)
            if 'error' in auth:
                return auth['error']
            user = auth['user']
            if hashlib.sha256(request.data['password'].encode()).hexdigest() != user.password:
                return JsonResponse({'message': 'Incorrect password'},
                                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['confirmation'] != 'DELETE':
                return JsonResponse({'message': 'Confirmation does not match'},
                                    status=status.HTTP_400_BAD_REQUEST)
            user.user_status = 'Deleted'
            user.user_status_updated_date = datetime.now()
            return JsonResponse({'message': 'Account marked for deletion'},
                                status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            