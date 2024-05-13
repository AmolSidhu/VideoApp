from django.core.management.base import BaseCommand
from django.db import connections

class Command(BaseCommand):

    def handle(self, *args, **options):
        with connections['default'].cursor() as cursor:
            cursor.execute(
                """
                -- Trigger for updating last_updated field of Credentials table
                CREATE OR REPLACE FUNCTION update_credentials_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_credentials_last_updated_insert
                AFTER INSERT ON core.credentials
                FOR EACH ROW
                EXECUTE FUNCTION update_credentials_last_updated();

                CREATE TRIGGER update_credentials_last_updated_update
                AFTER UPDATE ON core.credentials
                FOR EACH ROW
                EXECUTE FUNCTION update_credentials_last_updated();

                -- Trigger for updating last_updated field of Temp_Video table
                CREATE OR REPLACE FUNCTION update_temp_video_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_temp_video_last_updated_insert
                AFTER INSERT ON core.temp_video
                FOR EACH ROW
                EXECUTE FUNCTION update_temp_video_last_updated();

                CREATE TRIGGER update_temp_video_last_updated_update
                AFTER UPDATE ON core.temp_video
                FOR EACH ROW
                EXECUTE FUNCTION update_temp_video_last_updated();

                -- Trigger for updating last_updated field of Video table
                CREATE OR REPLACE FUNCTION update_video_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_video_last_updated_insert
                AFTER INSERT ON core.video
                FOR EACH ROW
                EXECUTE FUNCTION update_video_last_updated();

                CREATE TRIGGER update_video_last_updated_update
                AFTER UPDATE ON core.video
                FOR EACH ROW
                EXECUTE FUNCTION update_video_last_updated();

                -- Trigger for updating timestamp field of Video_Comments table
                CREATE OR REPLACE FUNCTION update_video_comments_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.timestamp = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_video_comments_timestamp_insert
                AFTER INSERT ON core.video_comments
                FOR EACH ROW
                EXECUTE FUNCTION update_video_comments_timestamp();

                CREATE TRIGGER update_video_comments_timestamp_update
                AFTER UPDATE ON core.video_comments
                FOR EACH ROW
                EXECUTE FUNCTION update_video_comments_timestamp();

                -- Trigger for updating timestamp field of Video_History table
                CREATE OR REPLACE FUNCTION update_video_history_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.timestamp = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_video_history_timestamp_insert
                AFTER INSERT ON core.video_history
                FOR EACH ROW
                EXECUTE FUNCTION update_video_history_timestamp();

                CREATE TRIGGER update_video_history_timestamp_update
                AFTER UPDATE ON core.video_history
                FOR EACH ROW
                EXECUTE FUNCTION update_video_history_timestamp();

                -- Trigger for updating last_updated field of Identifier table
                CREATE OR REPLACE FUNCTION update_identifier_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_identifier_last_updated_insert
                AFTER INSERT ON core.identifiers
                FOR EACH ROW
                EXECUTE FUNCTION update_identifier_last_updated();

                CREATE TRIGGER update_identifier_last_updated_update
                AFTER UPDATE ON core.identifiers
                FOR EACH ROW
                EXECUTE FUNCTION update_identifier_last_updated();

                -- Trigger for updating last_updated field of IdentifierTempTable table
                CREATE OR REPLACE FUNCTION update_identifier_temp_table_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_identifier_temp_table_last_updated_insert
                AFTER INSERT ON core.identifiers_temp_table
                FOR EACH ROW
                EXECUTE FUNCTION update_identifier_temp_table_last_updated();

                CREATE TRIGGER update_identifier_temp_table_last_updated_update
                AFTER UPDATE ON core.identifiers_temp_table
                FOR EACH ROW
                EXECUTE FUNCTION update_identifier_temp_table_last_updated();

                -- Trigger for updating last_updated field of WatchLocation table
                CREATE OR REPLACE FUNCTION update_watch_location_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    NEW.last_updated = CURRENT_TIMESTAMP;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER update_watch_location_last_updated_insert
                AFTER INSERT ON core.watch_location
                FOR EACH ROW
                EXECUTE FUNCTION update_watch_location_last_updated();

                CREATE TRIGGER update_watch_location_last_updated_update
                AFTER UPDATE ON core.watch_location
                FOR EACH ROW
                EXECUTE FUNCTION update_watch_location_last_updated();

                -- Trigger for updating last_updated field of Credentials table on DELETE
                CREATE OR REPLACE FUNCTION delete_credentials_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_credentials_last_updated
                AFTER DELETE ON core.credentials
                FOR EACH ROW
                EXECUTE FUNCTION delete_credentials_last_updated();

                -- Trigger for updating last_updated field of Temp_Video table on DELETE
                CREATE OR REPLACE FUNCTION delete_temp_video_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_temp_video_last_updated
                AFTER DELETE ON core.temp_video
                FOR EACH ROW
                EXECUTE FUNCTION delete_temp_video_last_updated();

                -- Trigger for updating last_updated field of Video table on DELETE
                CREATE OR REPLACE FUNCTION delete_video_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_video_last_updated
                AFTER DELETE ON core.video
                FOR EACH ROW
                EXECUTE FUNCTION delete_video_last_updated();

                -- Trigger for updating timestamp field of Video_Comments table on DELETE
                CREATE OR REPLACE FUNCTION delete_video_comments_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.timestamp = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_video_comments_timestamp
                AFTER DELETE ON core.video_comments
                FOR EACH ROW
                EXECUTE FUNCTION delete_video_comments_timestamp();

                -- Trigger for updating timestamp field of Video_History table on DELETE
                CREATE OR REPLACE FUNCTION delete_video_history_timestamp()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.timestamp = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_video_history_timestamp
                AFTER DELETE ON core.video_history
                FOR EACH ROW
                EXECUTE FUNCTION delete_video_history_timestamp();

                -- Trigger for updating last_updated field of Identifier table on DELETE
                CREATE OR REPLACE FUNCTION delete_identifier_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_identifier_last_updated
                AFTER DELETE ON core.identifiers
                FOR EACH ROW
                EXECUTE FUNCTION delete_identifier_last_updated();

                -- Trigger for updating last_updated field of IdentifierTempTable table on DELETE
                CREATE OR REPLACE FUNCTION delete_identifier_temp_table_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_identifier_temp_table_last_updated
                AFTER DELETE ON core.identifiers_temp_table
                FOR EACH ROW
                EXECUTE FUNCTION delete_identifier_temp_table_last_updated();

                -- Trigger for updating last_updated field of WatchLocation table on DELETE
                CREATE OR REPLACE FUNCTION delete_watch_location_last_updated()
                RETURNS TRIGGER AS $$
                BEGIN
                    OLD.last_updated = CURRENT_TIMESTAMP;
                    RETURN OLD;
                END;
                $$ LANGUAGE plpgsql;

                CREATE TRIGGER delete_watch_location_last_updated
                AFTER DELETE ON core.watch_location
                FOR EACH ROW
                EXECUTE FUNCTION delete_watch_location_last_updated();
                """
            )
