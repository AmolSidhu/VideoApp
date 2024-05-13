import unicodedata

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