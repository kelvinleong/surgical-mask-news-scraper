
class NewsFeedDao:
    TABLE_NAME = 'news_feed'

    # constructor
    def __init__(self, db):
        self.db = db['mask-news']
        self.collection = self.db[self.TABLE_NAME]

    def save(self, question):
        self.collection.insert_one(question.__dict__)

    def find(self, object_id):
        return self.collection.find_one(object_id)

    def find_all(self):
        return self.collection.find({})


class NewsFeed(object):
    def __init__(self, title="", update_time=None, content=""):
        self.title = title
        self.update_time = update_time
        self.content = content

    def get_title(self):
        return self.title

    def get_update_time(self):
        return self.update_time

    def get_content(self):
        return self.content

    def set_title(self, title):
        self.title = title

    def set_update_time(self, update_time):
        self.update_time = update_time

    def set_content(self, content):
        self.content = content
