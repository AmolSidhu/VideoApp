from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):

    def handle(self, *args, **options):
        with connections['default'].cursor() as cursor:
            cursor.execute(
            """
            -- Trigger for updating last_updated field of Credentials table on DELETE
            CREATE TRIGGER delete_credentials_last_updated
            AFTER DELETE ON core_credentials
            BEGIN
                UPDATE core_credentials SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating last_updated field of Temp_Video table on DELETE
            CREATE TRIGGER delete_temp_video_last_updated
            AFTER DELETE ON core_temp_video
            BEGIN
                UPDATE core_temp_video SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating last_updated field of Video table on DELETE
            CREATE TRIGGER delete_video_last_updated
            AFTER DELETE ON core_video
            BEGIN
                UPDATE core_video SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating timestamp field of Video_Comments table on DELETE
            CREATE TRIGGER delete_video_comments_timestamp
            AFTER DELETE ON core_video_comments
            BEGIN
                UPDATE core_video_comments SET timestamp = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating timestamp field of Video_History table on DELETE
            CREATE TRIGGER delete_video_history_timestamp
            AFTER DELETE ON core_video_history
            BEGIN
                UPDATE core_video_history SET timestamp = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating last_updated field of Identifier table on DELETE
            CREATE TRIGGER delete_identifier_last_updated
            AFTER DELETE ON core_identifiers
            BEGIN
                UPDATE core_identifiers SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating last_updated field of IdentifierTempTable table on DELETE
            CREATE TRIGGER delete_identifier_temp_table_last_updated
            AFTER DELETE ON core_identifiers_temp_table
            BEGIN
                UPDATE core_identifiers_temp_table SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;

            -- Trigger for updating last_updated field of WatchLocation table on DELETE
            CREATE TRIGGER delete_watch_location_last_updated
            AFTER DELETE ON core_watch_location
            BEGIN
                UPDATE core_watch_location SET last_updated = DATETIME('now') WHERE id = OLD.id;
            END;
            """
        )
