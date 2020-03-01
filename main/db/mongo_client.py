import pymongo


class MongoDB(object):
    def __init__(self):
        self.conn = pymongo.MongoClient('mongodb://root:root@localhost:27017/')

    def get_db_instance(self):
        return self.conn
