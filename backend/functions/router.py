class ReadWriteRouter:
    def db_for_read(self, model):
        return 'read_db'

    def db_for_write(self, model):
        return 'default'

    def allow_relation(self, obj1, obj2):
        db_list = ('default', 'read_db')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db in ['default', 'read_db']:
            return True
        return None

