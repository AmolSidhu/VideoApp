def get_video_list_query():
    return """
SELECT 
    v.title,
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    COALESCE(nsv.thumbnail_location, ssv.thumbnail_location) AS thumbnail_location,
    COALESCE(nsv.video_location, ssv.video_location) AS video_location,
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
FROM video v
LEFT JOIN (
    SELECT 
        video_instance_id AS video_id, 
        thumbnail_location, 
        video_location 
    FROM non_series_video
) nsv ON v.id = nsv.video_id
LEFT JOIN (
    SELECT 
        batch_instance_id AS video_id, 
        MIN(thumbnail_location) AS thumbnail_location, 
        MIN(video_location) AS video_location 
    FROM series_video
    GROUP BY batch_instance_id
) ssv ON v.id = ssv.video_id
INNER JOIN credentials u ON v.uploaded_by_id = u.id
WHERE v.current_status = 'Processing Completed'
AND v.private = FALSE
AND u.permission <= %s
ORDER BY rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT 10;
"""

def get_video_by_genre_query():
    return """
SELECT 
    v.title, 
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    COALESCE(nsv.thumbnail_location, ssv.thumbnail_location) AS thumbnail_location,
    COALESCE(nsv.video_location, ssv.video_location) AS video_location,
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
FROM video v
LEFT JOIN (
    SELECT 
        video_instance_id AS video_id, 
        thumbnail_location, 
        video_location 
    FROM non_series_video
) nsv ON v.id = nsv.video_id
LEFT JOIN (
    SELECT 
        batch_instance_id AS video_id, 
        MIN(thumbnail_location) AS thumbnail_location, 
        MIN(video_location) AS video_location 
    FROM series_video
    GROUP BY batch_instance_id
) ssv ON v.id = ssv.video_id
INNER JOIN credentials u ON v.uploaded_by_id = u.id
WHERE v.current_status = 'Processing Completed'
AND v.private = FALSE
AND u.permission <= %s
AND EXISTS (
    SELECT 1 FROM jsonb_array_elements_text(v.tags) AS tag
    WHERE tag = %s
)
ORDER BY rating_with_tiebreaker DESC, v.total_ratings DESC
LIMIT 5;
"""

def get_recently_viewed_query():
    return """
WITH latest_history AS (
    SELECT DISTINCT ON (vh.video_serial_id)
        vh.video_serial_id,
        vh.timestamp,
        vh.serial
    FROM core.video_history vh
    WHERE vh.user_id = %s
    ORDER BY vh.video_serial_id, vh.timestamp DESC
)
SELECT 
    v.title, 
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    COALESCE(nsv.thumbnail_location, sv.thumbnail_location) AS thumbnail_location,
    lh.timestamp,
    u.username as uploader_username,
    v.imdb_rating,
    v.description,
    CASE
        WHEN v.uploaded_by_id = %s THEN 1
        ELSE 0
    END AS user_match
FROM latest_history lh
JOIN core.video v ON v.id = lh.video_serial_id
LEFT JOIN core.non_series_video nsv ON nsv.video_instance_id = v.id
AND nsv.video_serial = lh.serial
LEFT JOIN core.series_video sv ON sv.batch_instance_id = v.id
AND sv.video_serial = lh.serial
JOIN core.credentials u ON v.uploaded_by_id = u.id
WHERE v.current_status = 'Processing Completed'
    AND v.private = FALSE
    AND u.permission <= %s
ORDER BY lh.timestamp DESC
LIMIT 5;
"""

def get_video_search_query():
    return """
SELECT DISTINCT ON (v.serial) 
    v.title,
    v.tags,
    v.directors,
    v.stars,
    v.writers,
    v.creators,
    v.serial,
    COALESCE(nsv.thumbnail_location, ssv.thumbnail_location) AS thumbnail_location,
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
FROM video v
LEFT JOIN non_series_video nsv ON v.id = nsv.video_instance_id
LEFT JOIN series_video ssv ON v.id = ssv.batch_instance_id
INNER JOIN credentials u ON v.uploaded_by_id = u.id
WHERE 
    (v.title ILIKE %s OR v.tags::text ILIKE %s)
    AND v.current_status = 'Processing Completed'
    AND v.private = FALSE
    AND u.permission <= %s
ORDER BY v.serial, v.title;
"""

