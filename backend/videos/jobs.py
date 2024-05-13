from apscheduler.schedulers.background import BackgroundScheduler
from moviepy.editor import VideoFileClip
from django.utils import timezone
import numpy as np
import bs4 as bs
import subprocess
import requests
import logging
import librosa
import json
import cv2
import os
import re
import av

from core.serializer import VideoSerializer, IdentifierSerializer
from .models import Video, TempVideo
from management.models import Identifier

logger = logging.getLogger(__name__)

def check_corruption_temp():
    videos = TempVideo.objects.filter(corruption_check_temp=False,
                                       current_status="File Uploaded")

    for video in videos:
        try:
            check = av.open(f'{video.video_location}{video.serial}.mp4')
            if not check or not check.streams.video:
                video.current_status = "Corrupted File"
                video.save()
                continue
            
            video.corruption_check_temp = True
            video.current_status = "Initial Corruption Checked"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during corruption check for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()
            
def start_corruption_temp():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_corruption_temp, 'interval', minutes=1)
    scheduler.start()

def convert_video():
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    videos = TempVideo.objects.filter(format_conversion=False,
                                       current_status="Initial Corruption Checked")
    
    for video in videos:
        try:
            output_path = os.path.join(directory['video_dir'], f'{video.serial}.mp4')
            command = [
                'ffmpeg',
                '-hwaccel', 'cuda',
                '-i', os.path.join(video.video_location, f'{video.serial}.mp4'),
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:v', '2M',
                '-vf', 'yadif',
                output_path
            ]
            
            subprocess.run(command)
            
            video.format_conversion = True
            video.current_status = "Format Converted"
            video.last_updated = timezone.now()
            video.video_location = directory['video_dir']
            video.save()
            
        except Exception as e:
            logger.error(f"Error during video {video.serial} conversion: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()

def start_converter():
    scheduler = BackgroundScheduler()
    scheduler.add_job(convert_video, 'interval', minutes=1)
    scheduler.start()
    
def check_corruption_data():
    videos = TempVideo.objects.filter(corruption_check_data=False,
                                       current_status="Format Converted")
    for video in videos:
        try:
            check = av.open(f'{video.video_location}{video.serial}.mp4')
            if not check or not check.streams.video:
                video.current_status = "Corrupted File"
                video.save()
                continue
            
            video.corruption_check_data = True
            video.current_status = "Data Corruption Checked"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during corruption check for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()
    
def start_corruption_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_corruption_data, 'interval', minutes=1)
    scheduler.start()

def imdb_data():
    videos = TempVideo.objects.filter(imdb_added=False,
                                       current_status="Data Corruption Checked")
    
    for video in videos:
        if video.imdb_link == '':
            video.current_status = "IMDB Passed"
            video.imdb_link_failed = True
            video.save()
            continue
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            
            response = requests.get(video.imdb_link, headers=headers)
            response.encoding = 'utf-8'
            html_content = response.text
            response.raise_for_status()
            soup = bs.BeautifulSoup(html_content, 'lxml')
            
            title = soup.find('h1').text
            
            
            try:
                description_tag = soup.find(attrs={'data-testid': 'plot'})

                if description_tag:
                    span_tags = description_tag.find_all('span')
                    
                    if len(span_tags) > 1:
                        description = span_tags[1].text.strip()
                    if len(span_tags) == 1:
                        description = span_tags[0].text.strip()
            except Exception as e:
                description = ''
                
            all_genres = []
            try:
                genre_tags = soup.find(attrs={'data-testid': 'genres'}).find_all('span')
                for genre_tag in genre_tags:
                    all_genres.append(genre_tag.text)
            except AttributeError:
                all_genres = []
                
            try:
                rating = soup.find(attrs={'data-testid': 'hero-rating-bar__aggregate-rating__score'}).text.strip().replace('/10', '')
            except AttributeError:
                rating = 0.0
            
            try:
                thumbnail_url = soup.find(attrs={'data-testid': 'hero-media__poster'}).find('img')['src']
                thumbnail_response = requests.get(thumbnail_url, headers=headers)
                thumbnail_filename = os.path.basename(thumbnail_url).replace(':', '_')
                thumbnail_filename = video.serial
                with open(f'{video.thumbnail_location}{thumbnail_filename}.jpg', 'wb') as f:
                    f.write(thumbnail_response.content)
            except Exception as e:
                thumbnail_filename = None
                
            breakers = [
                'Director',
                'Directors',
                'Stars',
                'Star',
                'Cast',
                'Casts',
                'Writer',
                'Writers',
                'Creator',
                'Creators'
                ]

            all_directors = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Directors?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Directors?$'))
            if primary_a_tag or primary_span_tag:
                if primary_a_tag:
                    primary_tag = primary_a_tag
                else:
                    primary_tag = primary_span_tag
                nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)
                skip_breaker = primary_tag.text.strip()
                for nested_tag in nested_tags:
                    nested_director = nested_tag.text.strip()
                    if nested_director:
                        if nested_director == skip_breaker:
                            continue
                        elif nested_director in breakers:
                            break
                        all_directors.append(nested_director)
                    else:
                        break
            
            all_writers = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Writers?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Writers?$'))
            if primary_a_tag or primary_span_tag:
                if primary_a_tag:
                    primary_tag = primary_a_tag
                else:
                    primary_tag = primary_span_tag
                nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)
                skip_breaker = primary_tag.text.strip()
                for nested_tag in nested_tags:
                    nested_writer = nested_tag.text.strip()
                    if nested_writer:
                        if nested_writer == skip_breaker:
                            continue
                        elif nested_writer in breakers:
                            break
                        all_writers.append(nested_writer)
                    else:
                        break
            
            all_stars = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Stars?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Stars?$'))
            if primary_a_tag or primary_span_tag:
                if primary_a_tag:
                    primary_tag = primary_a_tag
                else:
                    primary_tag = primary_span_tag
                nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)
                skip_breaker = primary_tag.text.strip()
                for nested_tag in nested_tags:
                    nested_star = nested_tag.text.strip()
                    if nested_star:
                        if nested_star == skip_breaker:
                            continue
                        if nested_star in breakers:
                            break
                        all_stars.append(nested_star)
                    else:
                        break
            
            all_creators = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Creators?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Creators?$'))
            if primary_a_tag or primary_span_tag:
                if primary_a_tag:
                    primary_tag = primary_a_tag
                else:
                    primary_tag = primary_span_tag
                nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)
                skip_breaker = primary_tag.text.strip()
                for nested_tag in nested_tags:
                    nested_creator = nested_tag.text.strip()
                    if nested_creator:
                        if nested_creator == skip_breaker:
                            continue
                        if nested_creator in breakers:
                            break
                        all_creators.append(nested_creator)
                    else:
                        break
   
            video.title = title
            video.description = (description)
            video.tags = (all_genres)
            video.main_tag = (all_genres[0])
            video.directors = (all_directors)
            video.writers = (all_writers)
            video.stars = (all_stars)
            video.creators = (all_creators)
            video.imdb_rating = (rating)
            video.imdb_added = True
            video.image_added = True
            video.current_status = "IMDB Passed"   
            video.last_updated = timezone.now()
            video.save()
            
            imdb_id_regex = r't{1}t\d+'
            imdb_id = re.search(imdb_id_regex, video.imdb_link).group()
            
            with open('directory.json', 'r') as f:
                directory = json.load(f)
                
            existing_identifier = Identifier.objects.filter(identifier=imdb_id)
            if existing_identifier.exists():
                pass
            else:         
                identifier_record = Identifier.objects.create(
                    identifier=imdb_id,
                    current_status="Added",
                    json_location=directory['json_records_dir']
                )
                serializer = IdentifierSerializer(identifier_record)
                         
        except Exception as e:
            logger.error(f"Error during IMDB data fetch for video {video.serial}: {str(e)}")
            
            if video.imdb_failed_attempts >= 3:
                video.imdb_failed_attempts += 1
                video.current_status = "IMDB Passed"
                video.imdb_added = True
                video.image_added = False
            else:
                video.imdb_failed_attempts += 1
            
            video.save()

def start_imdb_data():
    scheduler = BackgroundScheduler()
    scheduler.add_job(imdb_data, 'interval', minutes=1)
    scheduler.start()

def audio_profile():    
    videos = TempVideo.objects.filter(imdb_added=True,
                                       current_status="IMDB Passed")
    
    for video in videos:
        try:
            clip = VideoFileClip(f'{video.video_location}{video.serial}.mp4')
            audio_path = f'{video.video_location}{video.serial}.wav'
            clip.audio.write_audiofile(audio_path, codec='pcm_s16le')
            
            y, sr = librosa.load(audio_path, sr=None, mono=True)
            
            average_volume = np.mean(librosa.feature.rms(y=y))
            
            audio_profile = {
                'duration': clip.duration,
                'sample_rate': sr,
                'channels': y.shape[0],
                'average_volume': average_volume
            }
            
            audio_details = {key: float(value) if not isinstance(value, tuple) else value for key, value in audio_profile.items()}
            
            video.audio_details = audio_details
            video.audio_data_added = True
            video.current_status = "Audio Data Added"
            video.last_updated = timezone.now()
            video.save()
            
            os.remove(audio_path)
            
        except FileNotFoundError as e:
            logger.error(f"File not found error for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()
            
        except Exception as e:
            logger.error(f"Error during audio profile calculation for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()
                
def start_audio_profile():
    scheduler = BackgroundScheduler()
    scheduler.add_job(audio_profile, 'interval', minutes=1)
    scheduler.start()  

def visual_profile():
    logger.info("Calculating visual profiles started")
    
    videos = TempVideo.objects.filter(visual_data_added=False, current_status="Audio Data Added")
    
    for video in videos:
        try:
            cap = cv2.VideoCapture(f'{video.video_location}{video.serial}.mp4')
            if not cap.isOpened():
                logger.error(f"Failed to open video file {video.video_location}")
                continue
            
            total_saturation = 0
            frame_count = 0
            path = f'{video.thumbnail_location}{video.serial}.jpg'
            if path == None or video.imdb_link_failed == True or video.image_added == False:
            
                total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                target_frame = int(total_frames * 0.1)
                thumbnail_path = f'{video.thumbnail_location}{video.serial}.jpg'
                ret, frame = cap.read()
                if not ret:
                    logger.error("Failed to read frame")
                    continue
                
                cv2.imwrite(thumbnail_path, frame)
                video.thumbnail_location = thumbnail_path
                video.save()
                cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
            
            ret, frame = cap.read()
            if not ret:
                logger.error("Failed to read frame")
                continue
                
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            saturation = np.mean(hsv[:,:,1]) / 255.0
            total_saturation += saturation
            frame_count += 1
            
            if frame_count == 0:
                average_saturation = 0
            else:
                average_saturation = total_saturation / frame_count
            
            visual_profile_data = {
                'duration': cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS) if cap.get(cv2.CAP_PROP_FPS) != 0 else 0,
                'resolution': (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))),
                'frame_rate': cap.get(cv2.CAP_PROP_FPS),
                'average_saturation': average_saturation
            }

            video.visual_profile = visual_profile_data
            video.visual_data_added = True
            video.current_status = "Visual Data Added"
            video.last_updated = timezone.now()
            video.save()
            
        except Exception as e:
            logger.error(f"Error during visual profile calculation for video {video.serial}: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()



def start_visual_profile():
    scheduler = BackgroundScheduler()
    scheduler.add_job(visual_profile, 'interval', minutes=1)
    scheduler.start()

def completed_processing():
    videos = TempVideo.objects.filter(visual_data_added=True, audio_data_added=True, current_status="Visual Data Added")
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    for video in videos:
        try:
            video_instance = Video.objects.create(
                video_name=video.video_name,
                title=video.title,
                main_tag=video.main_tag,
                tags=video.tags,
                serial=video.serial,
                permission=video.permission,
                series=video.series,
                private=video.private,
                uploaded_by=video.uploaded_by,
                total_rating_score=video.total_rating_score,
                total_ratings=video.total_ratings,
                visual_profile=video.visual_profile,
                audio_profile=video.audio_profile,
                visual_details=video.visual_details,
                audio_details=video.audio_details,
                current_status="Processing Completed",
                uploaded_date=video.uploaded_date,
                last_updated=video.last_updated,
                description=video.description,
                directors=video.directors,
                stars=video.stars,
                writers=video.writers,
                creators=video.creators,
                imdb_link=video.imdb_link,
                imdb_rating=video.imdb_rating,
                video_location=video.video_location,
            )
            
            record = VideoSerializer(video_instance)
            
            os.remove(f'{directory['temp_videos_dir']}{video.serial}.mp4')
            
            video.delete()
            
        except Exception as e:
            logger.error(f"Error during video {video.serial} processing completion: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()

def start_processing_completion():
    scheduler = BackgroundScheduler()
    scheduler.add_job(completed_processing, 'interval', minutes=1)
    scheduler.start()

def failed_processing():
    videos = TempVideo.objects.filter(current_status="Failed to Process")
    
    for video in videos:
        try:
            video_instance = Video.objects.create(
                video_name=video.video_name,
                video_location=video.video_location,
                main_tag=video.main_tag,
                tags=video.tags,
                serial=video.serial,
                permission=video.permission,
                series=video.series,
                private=video.private,
                uploaded_by=video.uploaded_by,
                total_rating_score=video.total_rating_score,
                total_ratings=video.total_ratings,
                visual_profile=video.visual_profile,
                audio_profile=video.audio_profile,
                visual_details=video.visual_details,
                audio_details=video.audio_details,
                current_status="Failed Processing",
                uploaded_date=video.uploaded_date,
                last_updated=video.last_updated,
                description=video.description,
                directors=video.directors,
                stars=video.stars,
                writers=video.writers,
                creators=video.creators,
                imdb_link=video.imdb_link,
                imdb_rating=video.imdb_rating,
            )
            
            record = VideoSerializer(video_instance)
            
            os.remove(f'{video.video_location}{video.serial}.mp4')
            
            video.delete()
            
        except Exception as e:
            logger.error(f"Error during video {video.serial} processing failure: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()
            
def start_failed_processing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(failed_processing, 'interval', minutes=1)
    scheduler.start()

def corrupt_video():
    videos = TempVideo.objects.filter(current_status="Corrupted File")
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    for video in videos:
        try:
            video_instance = Video.objects.create(
                video_name=video.video_name,
                video_location=video.video_location,
                main_tag=video.main_tag,
                tags=video.tags,
                serial=video.serial,
                permission=video.permission,
                series=video.series,
                private=video.private,
                uploaded_by=video.uploaded_by,
                total_rating_score=video.total_rating_score,
                total_ratings=video.total_ratings,
                visual_profile=video.visual_profile,
                audio_profile=video.audio_profile,
                visual_details=video.visual_details,
                audio_details=video.audio_details,
                current_status="Failed Processing",
                uploaded_date=video.uploaded_date,
                last_updated=video.last_updated,
                description=video.description,
                directors=video.directors,
                stars=video.stars,
                creators=video.creators,
                writers=video.writers,
                imdb_link=video.imdb_link,
                imdb_rating=video.imdb_rating,
            )
            
            record = VideoSerializer(video_instance)
            
            location = directory['video_records_dir']
            
            os.remove(f'{video.video_location}{video.serial}.mp4')
            os.remove(f'{location}{video.serial}.mp4')
            
            video.delete()
            
        except Exception as e:
            logger.error(f"Error during video {video.serial} corruption: {str(e)}")
            
            if video.failed_attempts >= 3:
                video.failed_attempts += 1
                video.current_status = "Failed to Process"
            else:
                video.failed_attempts += 1
            
            video.save()

def start_corruption_processing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(corrupt_video, 'interval', minutes=1)
    scheduler.start()