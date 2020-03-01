import unittest
from datetime import datetime

from scrapy.selector import Selector

from main.news.mask_news import News
from main.news.news_feed import NewsFeed

news_list_xpath = '//*[@id="article-2553122"]/div/div[4]/div[1]/p'


class MaskNewsTest(unittest.TestCase):

    def test_crawl(self):
        with open("./news.html", encoding='utf-8') as f:
            news_p_list = Selector(text=f.read(), type='html').xpath(news_list_xpath)
            self.assertGreater(len(news_p_list), 0)

    def test_clear_title_format(self):
        text = "<p><u><strong>title</strong></u></p>"
        result = News.clear_format(Selector(text=text, type='html').xpath(".//p").get())
        self.assertEqual(result, "title")

    def test_clear_content_format(self):
        text = "<p>some content</p>"
        result = News.clear_format(Selector(text=text, type='html').xpath(".//p").get())
        self.assertEqual(result, "some content")

    def test_clear_update_time_format(self):
        text = "<p>【更新2月28日 18：59】</p>"
        result = News.clear_format(Selector(text=text, type='html').xpath(".//p").get())
        self.assertEqual(result, "【更新2月28日 18：59】")

    def test_update_time(self):
        text = "<p>【更新2月28日 18：59】</p>"
        news_scraper = News()
        feed = NewsFeed()
        result = news_scraper.update_time_handler(Selector(text=text, type='html').xpath(".//p"), feed)
        self.assertTrue(result)
        self.assertEqual(feed.get_update_time(), datetime.strptime("2020-2-28 18:59", "%Y-%m-%d %H:%M"))