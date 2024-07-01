import unicodedata
from django.http import JsonResponse
from rest_framework import status
import jwt
from user.models import Credentials
def normalize_unicode(text):
    return unicodedata.normalize('NFKD', text)


def json_format(title, release_year, motion_picture_rating, runtime, description,
                all_genres, rating, popularity, thumbnail_url, writers, directors,
                stars, creators, tv_series):
    return {
        'Title': title,
        'Release Year': release_year,
        'Motion Picture Rating': motion_picture_rating,
        'TV Series': tv_series,
        'Runtime': runtime,
        'Description': description,
        'Genres': all_genres,
        'Rating': rating,
        'Popularity': popularity,
        'Thumbnail URL': thumbnail_url,
        'Writers': writers,
        'Directors': directors,
        'Stars': stars,
        'Creators': creators
    }
    
def auth_check(token):
    if not token:
        return {'error': JsonResponse({'message': 'Invalid or missing token'},
                                      status=status.HTTP_403_FORBIDDEN)}
    try:
        payload = jwt.decode(token,
                             'SECRET_KEY',
                             algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return {'error': JsonResponse({'message': 'Token expired'},
                                      status=status.HTTP_403_FORBIDDEN)}
    
    user = Credentials.objects.filter(username=payload['username'],
                                      email=payload['email']).first()
    if not user:
        return {'error': JsonResponse({'message': 'User not found'},
                                      status=status.HTTP_404_NOT_FOUND)}
    return {'user': user}