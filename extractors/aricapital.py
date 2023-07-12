from datetime import datetime, timezone, timedelta
import pytz
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import re

#from selenium import webdriver
#from selenium.webdriver import ChromeOptions
#from selenium.webdriver.common.by import By
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.common.exceptions import TimeoutException
#from selenium.common.exceptions import NoSuchElementException
#co = ChromeOptions()

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
localtime = pytz.timezone("Asia/Krasnoyarsk")
fua = UserAgent(verify_ssl=False)
headers = {'User-Agent': fua.random}

class Extractor:
    __scraped_data = None
    __url = None

    def __init__(self, url):
        self.__url = url 

    def get_data(self, delta = 30):
        
        if self.__scraped_data is not None:

            startdate = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=localtime) - timedelta(delta)
            output_list = []
        
            for section in self.__scraped_data:
                section_data = [e for e in section[1] if e[1] >= startdate]
                if len(section_data) > 0:
                    output_list.append([section[0], section_data])

            return output_list
        else:
            return []

    def __get_date(self, tag):
        dates = re.search('(?P<date>\d{2}.\d{2}.\d{4})', tag)
        times = re.search('(?P<time>\d{2}:\d{2})', tag)
        dtstring = '01.01.1970 00:00'
        if dates is not None:
            dtstring = dates['date']
            if times is not None:
                dtstring = dtstring + ' ' + times['time']
            else:
                dtstring = dtstring + ' 00:00'
        return localtime.localize(datetime.strptime(dtstring, '%d.%m.%Y %H:%M'))
        
    def __extract_element(self, doc):
        a_tag = doc.select_one('*.doc__title a')
        if a_tag:
            href = a_tag['href']
            text = a_tag.string
            date_span = doc.select_one('div.doc__info span.doc__published')
            if date_span:
                date = self.__get_date(date_span.string)
            else:
                date = self.__get_date(text)
            return (text, date, href)
        else:
            return None

    def __parse_contents(self, soup):
        for docs in soup.select('div.docs'):
            doclist = []
            h2_tag = docs.find_previous_sibling('h2', class_='content__title')
            if h2_tag:
                caption = h2_tag.string
            else:
                caption = 'Раскрытие информации'
            for doc in docs.select('div.doc:has(a)'):
                result = self.__extract_element(doc)
                if result:
                    doclist.append(result)

            if self.__scraped_data is None:
                self.__scraped_data = [] 
                self.__scraped_data.append([caption, doclist])
            else:
                self.__scraped_data.append([caption, doclist])

    def scrape(self):
        response = requests.get(self.__url, headers=headers, verify=False)
        s = re.findall('(https?://[A-Za-z_0-9.-]+)/.*', response.url)
        self.__domain = s[0]
        html = response.content
        soup = BeautifulSoup(html, 'html.parser')
        self.__parse_contents(soup.select_one('div.content'))
        for docs in soup.select('div.content div.docs'):
            next_sibling = docs.next_sibling
            if next_sibling.name == 'a' and 'Архив' in next_sibling.string:
                response = requests.get(next_sibling['href'], headers=headers, verify=False)
                html = response.content
                soup = BeautifulSoup(html, 'html.parser')
                self.__parse_contents(soup.select_one('div.content'))
