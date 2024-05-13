from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import bs4 as bs
import requests
import re

from .models import Identifier, IdentifierTempTable
from videos.models import VideoGenre, Video
from functions.function import normalize_unicode, json_format
from core.serializer import IdentifierSerializer, VideoGenresSerializer



def add_identifiers():
    temp_data = IdentifierTempTable.objects.all()
    
    with open('directory.json', 'r') as f:
        directory = json.load(f)
    
    for data in temp_data:
        file_path = data.file_location + data.temp_name + '.json'
        with open(file_path, 'r') as f:
            entries = json.load(f)
            for entry in entries:
                try:
                    existing_identifier = Identifier.objects.filter(
                        identifier=entry).first()
                    if existing_identifier is None:
                        identify_obj = Identifier.objects.create(
                            identifier=entry,
                            current_status="Added",
                            json_location=directory['json_records_dir']
                        )
                        serializer = IdentifierSerializer(identify_obj)
                except Exception as e:
                    print(e)
                    pass
            f.close()
            os.remove(file_path)
            data.delete()

def start_identifiers():
    scheduler = BackgroundScheduler()
    scheduler.add_job(add_identifiers, 'interval', minutes=1)
    scheduler.start()

def create_json_record():
    identifiers = Identifier.objects.filter(current_status="Added")[:100]
    
    for identifier in identifiers:
        title = 'N/A'
        release_year = 'N/A'
        motion_picture_rating = 'N/A'
        runtime = 'N/A'
        description = 'N/A'
        all_genres = 'N/A'
        rating = 'N/A'
        popularity = 'N/A'
        thumbnail_url = 'N/A'
        all_writers = 'N/A'
        all_directors = 'N/A'
        all_stars = 'N/A'
        all_creators = 'N/A'
        tv_series = False

        rating_patterns = [
            'G', 'PG', 'PG-13', 'R',
            'NC-17', 'TV-Y', 'TV-Y7',
            'TV-G', 'TV-PG', 'TV-14',
            'TV-MA', 'N/A', 'UR',
            'Not Rated', 'Unrated'
            ]
        
        rating_pattern = re.compile(r'\b(?:' + '|'.join(
            map(re.escape, rating_patterns)) + r')\b')
        
        imdb_base_url = 'https://www.imdb.com'
        imdb_movie_url = '/title/'
        
        headers = {
            'User-Agent':
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                  }

        url = imdb_base_url + imdb_movie_url + identifier.identifier

        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        html_content = response.text
        soup = bs.BeautifulSoup(html_content, 'lxml')
        
        try:
            
            title = normalize_unicode(soup.find('h1').text.strip())
            h1_tag = soup.find('h1')
            stat_ul = h1_tag.find_next('ul')
            if stat_ul:
                stats = stat_ul.find_all('li')
                tv_series = False

                for stat in stats:
                    text = stat.text.strip()

                    if text == 'TV Series':
                        tv_series = True
                        continue
                    
                    try:
                        release_year_match = re.search(r'\b\d{4}(?:-\d{4})?\b', text)
                        if release_year_match:
                            release_year = normalize_unicode(
                                release_year_match.group())
                    except AttributeError:
                        release_year = 'N/A'

                    try:
                        motion_picture_rating_match = rating_pattern.search(text)
                        if motion_picture_rating_match:
                            motion_picture_rating = normalize_unicode(
                                motion_picture_rating_match.group())
                    except AttributeError:
                        motion_picture_rating = 'N/A'
                        
                    try:
                        runtime_match = re.search(r'\b(?:\d+h\s\d+m|\d+m|\d+h)\b', text)
                        if runtime_match:
                            runtime = normalize_unicode(runtime_match.group())
                    except AttributeError:
                        runtime = 'N/A'

                    try:
                        description_tag = soup.find(attrs={'data-testid': 'plot'})

                        if description_tag:
                            span_tags = description_tag.find_all('span')
                            
                            if len(span_tags) > 1:
                                description = span_tags[1].text.strip()
                            if len(span_tags) == 1:
                                description = span_tags[0].text.strip()
                    except AttributeError:
                        description = 'N/A'
            
            try:
                all_genres = []
                genre_tags = soup.find(attrs={'data-testid': 'genres'}).find_all('span')
                for genre_tag in genre_tags:
                    all_genres.append(normalize_unicode(genre_tag.text))
            except AttributeError:
                all_genres = 'N/A'

            try:
                rating = normalize_unicode(soup.find(
                    attrs={'data-testid': 'hero-rating-bar__aggregate-rating__score'}
                    ).text.strip().replace('/10', ''))
            except AttributeError:
                rating = 'N/A'

            try:
                popularity = normalize_unicode(soup.find(
                    attrs={'data-testid': 'hero-rating-bar__popularity__score'}
                    ).text.strip().replace(',', ''))
            except AttributeError:
                popularity = 'N/A'

            try:
                thumbnail_url = normalize_unicode(soup.find(
                    attrs={'data-testid': 'hero-media__poster'}
                    ).find('img')['src'])
            except AttributeError:
                thumbnail_url = 'N/A'

            breakers = [
                'Director', 'Directors', 'Stars',
                'Star', 'Cast', 'Casts', 'Writer',
                'Writers', 'Creator', 'Creators'
                ]

            all_writers = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Writers?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Writers?$'))

            try:
                if primary_a_tag or primary_span_tag:
                    if primary_a_tag:
                        primary_tag = primary_a_tag
                    else:
                        primary_tag = primary_span_tag

                    nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)

                    for nested_tag in nested_tags:
                        nested_writer = normalize_unicode(nested_tag.text.strip())
                        nested_href = nested_tag.get('href')
                        if nested_writer:
                            if nested_writer in breakers:
                                break
                            all_writers.append({'name': nested_writer, 'url': imdb_base_url + nested_href})
                        else:
                            break
            except AttributeError:
                all_writers = 'N/A'

            all_directors = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Directors?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Directors?$'))

            try: 
                if primary_a_tag or primary_span_tag:
                    if primary_a_tag:
                        primary_tag = primary_a_tag
                    else:
                        primary_tag = primary_span_tag

                    nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)

                    for nested_tag in nested_tags:
                        nested_director = normalize_unicode(nested_tag.text.strip())
                        nested_href = nested_tag.get('href')
                        if nested_director:
                            if nested_director in breakers:
                                break
                            all_directors.append({'name': nested_director, 'url': imdb_base_url + nested_href})
                        else:
                            break
            except AttributeError:
                all_directors = 'N/A'

            all_stars = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Stars?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Stars?$'))

            try:
                if primary_a_tag or primary_span_tag:
                    if primary_a_tag:
                        primary_tag = primary_a_tag
                    else:
                        primary_tag = primary_span_tag

                    nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)

                    for nested_tag in nested_tags:
                        nested_star = normalize_unicode(nested_tag.text.strip())
                        nested_href = nested_tag.get('href')
                        if nested_star:
                            if nested_star in breakers:
                                break
                            all_stars.append({'name': nested_star, 'url': imdb_base_url + nested_href})
                        else:
                            break
            except AttributeError:
                all_stars = 'N/A'

            all_creators = []
            primary_a_tag = soup.find('a', string=re.compile(r'^Creators?$'))
            primary_span_tag = soup.find('span', string=re.compile(r'^Creators?$'))

            try:
                if primary_a_tag or primary_span_tag:
                    if primary_a_tag:
                        primary_tag = primary_a_tag
                    else:
                        primary_tag = primary_span_tag

                    nested_tags = primary_tag.find_all_next(['a', 'span'], recursive=False)

                    for nested_tag in nested_tags:
                        nested_creator = normalize_unicode(nested_tag.text.strip())
                        nested_href = nested_tag.get('href')
                        if nested_creator:
                            if nested_creator in breakers:
                                break
                            all_creators.append({'name': nested_creator, 'url': imdb_base_url + nested_href})
                        else:
                            break
            except AttributeError:
                all_creators = 'N/A'

            json_file = json_format(title=title,
                                    release_year=release_year,
                                    motion_picture_rating=motion_picture_rating,
                                    runtime=runtime, description=description,
                                    all_genres=all_genres, rating=rating,
                                    popularity=popularity,
                                    thumbnail_url=thumbnail_url,
                                    writers=all_writers,
                                    directors=all_directors,
                                    stars=all_stars,
                                    creators=all_creators,
                                    tv_series=tv_series)

            with open(f'{identifier.json_location}{identifier.identifier}.json',
                      'w', encoding='utf-8') as f:
                json.dump(json_file, f, indent=4, ensure_ascii=False)
            
            identifier.current_status = "Record Created"
            identifier.title = title
            identifier.save()

        except Exception as e:
            print(e)
            print(f'Error: {identifier.identifier}')
            identifier.delete()

def start_json_record():
    scheduler = BackgroundScheduler()
    scheduler.add_job(create_json_record, 'interval', minutes=1)
    scheduler.start()

def check_existing_genres():
    VideoGenre.objects.all().delete()

    genres = Video.objects.filter(private=False).all()
    genre_dict = {}
    known_genres = ['Action', 'Adventure', 'Animation', 'Biography', 'Comedy',
                    'Crime', 'Documentary', 'Drama', 'Family', 'Fantasy',
                    'Film-Noir', 'History', 'Horror', 'Music', 'Musical',
                    'Mystery', 'Romance', 'Sci-Fi', 'Sport', 'Thriller',
                    'War', 'Western']
    for video in genres:
        tags = video.tags if isinstance(video.tags, list) else []
        for tag in tags:
            if tag in genre_dict:
                genre_dict[tag]['number_of_public_records'] += 1
            else:
                custom = tag not in known_genres
                genre_dict[tag] = {
                    'genre': tag,
                    'custom': custom,
                    'number_of_public_records': 1
                }
    for genre_data in genre_dict.values():
        added_genre = VideoGenre.objects.create(**genre_data)
        serializer = VideoGenresSerializer(added_genre)

def start_genre_check():
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_existing_genres, 'interval', minutes=1)
    scheduler.start()
    
