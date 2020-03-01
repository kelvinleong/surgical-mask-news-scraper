from time import sleep
import datetime

from scrapy import Selector

from main.news.news_feed import NewsFeed, NewsFeedDao
from main.browser_driver.driver import Driver
from main.db.mongo_client import MongoDB

url = 'http://inews.hket.com/article/2553122/%E3%80%90%E5%8F%A3%E7%BD%A9%E9%9B%A3%E6%B1%82%E3%80%91%E5%8F%A3%E7%BD%A9' \
      '%E5%93%AA%E8%A3%A1%E8%B2%B7%E3%80%80%E5%8F%A3%E7%BD%A9%E8%BF%94%E8%B2%A8%E6%9C%80%E6%96%B0%E6%83%85%E6%B3%81' \
      '%E4%B8%80%E6%96%87%E7%9C%8B%E6%B8%85%EF%BC%88%E4%B8%8D%E6%96%B7%E6%9B%B4%E6%96%B0%EF%BC%89'


news_list_xpath = "//*[@id='article-2553122']/div/div[4]/div[1]/p"

title_pattern_1 = ".//u"
title_pattern_2 = ".//strong"


class Cache(object):
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key, None)

    def put(self, key, content):
        self.cache[key] = content

    def delete(self, key):
        if key in self.cache:
            del self.cache[key]

    def size(self):
        return len(self.cache)


class News(object):
    def __init__(self):
        self.driver = Driver().driver
        self.cache = Cache()
        self.news_feed_dao = NewsFeedDao(MongoDB().get_db_instance())
        self.title_pattern = title_pattern_1

    @staticmethod
    def convert_to_time(date_str=""):
        now = datetime.datetime.now()
        try:
            # tricky part (records before 31/01 did not contain year information)
            if "日" not in date_str:
                date_str = date_str.replace(" ", "") \
                    .replace("【", "").replace("】", "") \
                    .replace("更新時間：", "2020-1-31 ") \
                    .replace("：", ":").replace("︰", ":")
            else:
                date_str = date_str[1:15].replace(" ", "") \
                    .replace("【", "").replace("】", "") \
                    .replace("更新", str(now.year) + "-") \
                    .replace("時間", "") \
                    .replace("月", "-").replace("日", " ") \
                    .replace("：", ":").replace("︰", ":")
            return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M")
        except Exception:
            return now

    @staticmethod
    def clear_format(text):
        return text.replace("<p>", "").replace("</p>", "")\
            .replace("<u><strong>", "").replace("</strong></u>", "")

    def title_handler(self, p, feed):
        # try to find title first
        try:
            title = p.xpath(self.title_pattern)[0].get()
            if feed.get_title() and feed.get_content():
                self.check_and_save_feed(feed)
                # reset all fields title, update_time, content in feed
                feed.set_content("")
                feed.set_title("")
                feed.set_update_time(None)

            feed.set_title(self.clear_format(title))
            return True
        except Exception:
            return False

    def update_time_handler(self, p, feed):
        text = self.clear_format(p.get())
        if text.startswith("更新", 1):
            if feed.get_title() and feed.get_content() and feed.get_update_time():
                self.check_and_save_feed(feed)
                # reset update time and content for one title may contain multiple tweets
                feed.set_update_time(None)
                feed.set_content("")

            # update_time
            feed.set_update_time(self.convert_to_time(text))
            return True
        else:
            return False

    def content_handler(self, p, feed):
        # content
        if feed.get_title():
            if "＝＝＝＝＝＝＝" in p.get() or "===" in p.get():
                self.title_pattern = title_pattern_2
            feed.set_content(feed.get_content() + "\n" + self.clear_format(p.get()))

    def check_and_save_feed(self, feed):
        tk = str(hash(feed.get_title() + str(feed.get_update_time().time())))
        if not self.cache.get(tk):
            self.news_feed_dao.save(NewsFeed(feed.get_title(), feed.get_update_time(), feed.get_content()))
            self.cache.put(tk, feed.__dict__)

    def parse_news(self, content):
        # tree = html.fromstring(content)
        news_p_list = Selector(text=content, type="html").xpath(news_list_xpath)
        feed = NewsFeed()

        for p in news_p_list:
            if self.title_handler(p, feed):
                continue
            if self.update_time_handler(p, feed):
                continue
            self.content_handler(p, feed)

    def crawl(self):
        self.driver.get(url)
        while True:
            self.parse_news(self.driver.page_source)
            print("{:d} news are scrapped".format(self.cache.size()))
            sleep(120)
            self.driver.refresh()

    def pre_cache(self):
        news_list = self.news_feed_dao.find_all()
        for news in news_list:
            tk = str(hash(news.get_title() + str(news.get_update_time().time())))
            self.cache.put(tk, news)


def main():
    news = News()
    news.pre_cache()
    news.crawl()


if __name__ == "__main__":
    main()
