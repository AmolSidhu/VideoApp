from django.http import JsonResponse
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime

from .models import Credentials

import hashlib
import jwt
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
def register(request):
    try:
        if request.method == 'POST':
            existing_user = Credentials.objects.filter(Q(username=request.data['username']) | Q(email=request.data['email'])).first()
            if existing_user and existing_user.username == request.data['username']:
                response = JsonResponse({'msg': 'Username already exists'},
                                        status=status.HTTP_409_CONFLICT)
            if existing_user and existing_user.email == request.data['email']:
                response = JsonResponse({'msg': 'Email already exists'},
                                        status=status.HTTP_409_CONFLICT)
            else:
                if str(request.data['password']) != str(request.data['confirmPassword']):
                    response = JsonResponse({'msg': 'Passwords do not match'},
                                            status=status.HTTP_400_BAD_REQUEST)
                    return response
                else:
                    password = hashlib.sha256(request.data['password'].encode()).hexdigest()
                    new_user = Credentials.objects.create(
                        username=request.data['username'],
                        email=request.data['email'],
                        password=password,
                        verification_code=1234
                    )
                    new_user.save()
                    response = JsonResponse({'msg': 'User registered successfully'},
                                            status=status.HTTP_200_OK)
        return response
    except Exception as e:
        logging.error(f"Error during registration: {str(e)}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def verification(request):
    try:
        if request.method == 'PATCH':
            user = Credentials.objects.filter(email=request.data['email']).first()
            if request.data['verificationCode'] == user.verification_code:
                user.is_verified = True
                user.save()
                response = JsonResponse({'msg': 'User verified successfully'},
                                        status=status.HTTP_200_OK)
            else:
                response = JsonResponse({'msg': 'Invalid verification code'},
                                        status=status.HTTP_400_BAD_REQUEST)
        return response
    except Exception as e:
        logging.error(f"Error during verification: {str(e)}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def login(request):
    try:
        if request.method == 'PATCH':
            try:
                user = Credentials.objects.get(email=request.data['email'])
            except Credentials.DoesNotExist:
                return JsonResponse({'msg': 'User not found'},
                                    status=status.HTTP_404_NOT_FOUND)
            if not user.is_verified:
                return JsonResponse({'msg': 'User not verified'},
                                    status=status.HTTP_401_UNAUTHORIZED)
                
            correct_password = hashlib.sha256(request.data['password'].encode()).hexdigest() == user.password
            if not correct_password:
                return JsonResponse({'msg': 'Incorrect password'},
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                user.last_login = datetime.datetime.now()
                user.save()
                payload = {
                    'username': user.username,
                    'email': user.email
                }
                token = jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
                return JsonResponse({'token': token, 'msg': 'Logged in successfully'},
                                         status=status.HTTP_200_OK)
    except Exception as e:
        logging.error(f"Error during login: {str(e)}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PATCH'])
def logout(request):
    try:
        if request.method == 'PATCH':
            response = Response()
            response.delete_cookie('token')
            response['message'] = 'Logged out successfully'
            response.status_code = status.HTTP_200_OK
            return response
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        return Response({'message': 'Internal server error'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
