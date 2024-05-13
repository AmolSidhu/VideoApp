from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):

    def handle(self, *args, **options):
        with connections['default'].cursor() as cursor:
            cursor.execute(
            """
            -- Trigger for updating last_updated field of Credentials table
            CREATE TRIGGER update_credentials_last_updated_insert
            AFTER INSERT ON credentials
            BEGIN
                UPDATE credentials SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_credentials_last_updated_update
            AFTER UPDATE ON credentials
            BEGIN
                UPDATE credentials SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of Temp_Video table
            CREATE TRIGGER update_temp_video_last_updated_insert
            AFTER INSERT ON core_temp_video
            BEGIN
                UPDATE core_temp_video SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_temp_video_last_updated_update
            AFTER UPDATE ON core_temp_video
            BEGIN
                UPDATE core_temp_video SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of Video table
            CREATE TRIGGER update_video_last_updated_insert
            AFTER INSERT ON core_video
            BEGIN
                UPDATE core_video SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_video_last_updated_update
            AFTER UPDATE ON core_video
            BEGIN
                UPDATE core_video SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of Video_Comments table
            CREATE TRIGGER update_video_comments_last_updated_insert
            AFTER INSERT ON core_video_comments
            BEGIN
                UPDATE core_video_comments SET timestamp = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_video_comments_last_updated_update
            AFTER UPDATE ON core_video_comments
            BEGIN
                UPDATE core_video_comments SET timestamp = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of Video_History table
            CREATE TRIGGER update_video_history_last_updated_insert
            AFTER INSERT ON core_video_history
            BEGIN
                UPDATE core_video_history SET timestamp = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_video_history_last_updated_update
            AFTER UPDATE ON core_video_history
            BEGIN
                UPDATE core_video_history SET timestamp = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating number_of_public_records field of Video_Genres table
            CREATE TRIGGER update_video_genres_public_records
            AFTER INSERT ON core_video_genres
            BEGIN
                UPDATE core_video_genres SET number_of_public_records = (
                    SELECT COUNT(*) FROM core_video WHERE core_video.main_tag = NEW.genre
                ) WHERE genre = NEW.genre;
            END;

            -- Trigger for updating last_updated field of Identifier table
            CREATE TRIGGER update_identifier_last_updated_insert
            AFTER INSERT ON core_identifiers
            BEGIN
                UPDATE core_identifiers SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_identifier_last_updated_update
            AFTER UPDATE ON core_identifiers
            BEGIN
                UPDATE core_identifiers SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of IdentifierTempTable table
            CREATE TRIGGER update_identifier_temp_table_last_updated_insert
            AFTER INSERT ON core_identifiers_temp_table
            BEGIN
                UPDATE core_identifiers_temp_table SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_identifier_temp_table_last_updated_update
            AFTER UPDATE ON core_identifiers_temp_table
            BEGIN
                UPDATE core_identifiers_temp_table SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            -- Trigger for updating last_updated field of WatchLocation table
            CREATE TRIGGER update_watch_location_last_updated_insert
            AFTER INSERT ON core_watch_location
            BEGIN
                UPDATE core_watch_location SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;

            CREATE TRIGGER update_watch_location_last_updated_update
            AFTER UPDATE ON core_watch_location
            BEGIN
                UPDATE core_watch_location SET last_updated = DATETIME('now') WHERE id = NEW.id;
            END;
            """
)