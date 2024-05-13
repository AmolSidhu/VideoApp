from rest_framework.decorators import api_view
from rest_framework import status
from django.http import JsonResponse
from secrets import token_hex

import logging
import json
import jwt

from user.models import Credentials
from videos.models import Video

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
            videos = Video.objects.filter(user=user).all()[:5]
            return JsonResponse({'videos': videos},
                                status=status.HTTP_200_OK)   
    except Exception as e:
        logging.error(f"Error during video upload: {str(e)}")
        return JsonResponse({'message': 'Internal server error'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
