# -*- coding: UTF-8 -*-
__author__ = "double k"
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import datetime
import re
import time
from urllib.parse import quote
from pyquery import PyQuery as pq

# 抓取腾讯数码 手机栏目数据
class PhoneNews:
    # 初始化
    def __init__(self, baseUrl = None, waitTime = 20):
        # 爬取链接
        self.baseUrl = baseUrl
        # webdriver对象
        self.browser = None
        # WebDriverWait对象
        self.wait = None
        # 爬取html主体
        self.html = None
        # 等待时间
        self.waitTime = waitTime
        # 抓取总条数
        self.count = 0
    # 获取标签
    def getTags(self, item):
        i = 0
        tags = []
        execute = True
        while execute == True:
            tag = item('.tag').eq(i).text()
            if tag:
                tags.append(tag)
                i += 1
            else:
                execute = False
        return tags
    # 补齐链接
    def complementLink(self, url):
        if url:
            return "https:" + url
        else:
            return url
    # 获取图片
    def getImages(self, item):
        i = 0
        images = []
        while i < 3:
            image = self.complementLink(item('.picture').eq(i).attr.src)
            if image:
                images.append(image)
            i += 1
        return images
    """
        滑动滚动条加载所有数据
        如果waitForGetAllData()没有获取到想要的结果，则继续滚动
    """
    def moveBottom(self):
        jsCode = "var q=document.documentElement.scrollTop=100000"
        self.browser.execute_script(jsCode)
        self.waitForGetAllData()
    # 判断是否加载完全部数据 出现返回腾讯首页字样
    def waitForGetAllData(self):
        try:
            self.wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '#load-more > a')
                )
            )
        except TimeoutException:
            self.moveBottom()
    # 根据时间计算发布日期，如果没有获取到发布时间责默认半天前发布
    def getCreateTime(self, time):
        minuend = 0
        it = re.findall(re.compile('[0-9]{0,}'), time)
        if str(time) == "昨天":
            minuend = 24
        elif len(it) > 0:
            minuend = it[0]
        else:
            minuend = 12

        now = datetime.datetime.now()

        return (now - datetime.timedelta(hours=int(minuend))).strftime("%Y-%m-%d %H:%M:%S")
    # 获取非图片新闻
    def getWithoutPicNews(self):
        withoutPicItems = self.html("#List .list .item").items()
        for withoutPicItem in withoutPicItems:
            title = withoutPicItem.find('h3').text()
            if title:
                time = withoutPicItem.find('.time').text()
                product = {
                    'title': title,
                    'images': self.complementLink(withoutPicItem.find('img').attr.src),
                    'detail_url': withoutPicItem.find('.picture').attr.href,
                    'from': withoutPicItem.find(".source").text(),
                    'tags': self.getTags(withoutPicItem),
                    'category': withoutPicItem.find('.cate').text(),
                    'cmt': withoutPicItem.find(".cmt").text(),
                    'date': self.getCreateTime(time)
                }
                self.count += 1
                print(product)
    # 获取图片新闻
    def getWithPicNews(self):
        withPicItems = self.html("#List .list .item-pics").items()
        for withPicItem in withPicItems:
            title = withPicItem.find('h3').text()
            if title:
                time = withPicItem.find('.time').text()
                product = {
                    'title': title,
                    'images': self.getImages(withPicItem),
                    'detail_url': withPicItem.find('.pics').attr.href,
                    'from': withPicItem.find(".source").text(),
                    'tags': self.getTags(withPicItem),
                    'category': withPicItem.find('.cate').text(),
                    'cmt': withPicItem.find(".cmt").text(),
                    'date': self.getCreateTime(time)
                }
                self.count += 1
                print(product)

    # 关闭webdriver对象
    def close(self):
        self.browser.quit()

    # 初始化类中信息
    def main(self, isHeadLess=True):
        if self.baseUrl == None:
            print("请输入有效URL")
            return
        if isHeadLess == True:
            chromeOptions = webdriver.ChromeOptions()
            chromeOptions.add_argument("--headless")
            self.browser = webdriver.Chrome(chrome_options=chromeOptions)
        else:
            self.browser = webdriver.Chrome()

        self.wait = WebDriverWait(self.browser, self.waitTime)
        self.browser.get(self.baseUrl)
        self.waitForGetAllData()
        time.sleep(self.waitTime)
        html = self.browser.page_source
        self.html = pq(html)
        # self.getWithoutPicNews()
        # self.getWithPicNews()
url = "https://new.qq.com/ch2/phone"
phoneNews = PhoneNews(url, 30)
phoneNews.main(isHeadLess=True)
phoneNews.getWithoutPicNews()
phoneNews.getWithPicNews()
phoneNews.close()
print("-------共获取到", phoneNews.count, "条数据-------")

