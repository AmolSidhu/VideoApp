def get_video_list_query(user_id, viewer_permission_level):
    return """
SELECT 
    v.video_name, 
    v.title,
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    v.thumbnail_location,
    (%s || v.thumbnail_location || v.serial || '.jpg') AS image_url,
    u.username as uploader_username,
    v.imdb_rating,
    v.description,
    CASE
        WHEN v.total_ratings = 0 THEN 0
        ELSE v.total_rating_score / v.total_ratings
    END AS rating_with_tiebreaker,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
FROM core.video v
INNER JOIN core.credentials u ON v.uploaded_by_id = u.id
WHERE v.current_status = 'Processing Completed'
AND v.private = FALSE
AND u.permission <= %s
ORDER BY rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT 10;
"""

def get_video_by_genre_query():
    return """
SELECT 
    v.video_name, 
    v.title,
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    v.thumbnail_location,
    v.video_location,
    u.username as uploader_username,
    v.imdb_rating,
    v.description,
    CASE
        WHEN v.total_ratings = 0 THEN 0
        ELSE v.total_rating_score / v.total_ratings
    END AS rating_with_tiebreaker,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
FROM core.video v
INNER JOIN core.credentials u ON v.uploaded_by_id = u.id
WHERE v.current_status = 'Processing Completed'
AND v.private = FALSE
AND u.permission <= %s
AND %s IN (SELECT jsonb_array_elements_text(tags))
ORDER BY rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT 5;
"""

def get_recently_viewed_query():
    return """
    SELECT 
        v.video_name, 
        v.title,
        v.tags,
        v.directors,
        v.stars,
        v.writers,
        v.creators,
        v.serial,
        v.thumbnail_location,
        vh.timestamp,
        (%s || v.thumbnail_location || v.serial || '.jpg') AS image_url,
        u.username as uploader_username,
        v.imdb_rating,
        v.description,
        CASE
            WHEN v.uploaded_by_id = %s THEN 1
            ELSE 0
        END AS user_match
    FROM core.video v
    INNER JOIN core.video_history vh ON v.id = vh.video_serial_id
    INNER JOIN core.credentials u ON v.uploaded_by_id = u.id
    WHERE vh.user_id = %s
    AND v.current_status = 'Processing Completed'
    AND v.private = FALSE
    AND u.permission <= %s
    ORDER BY vh.timestamp DESC
    LIMIT 10;
    """
