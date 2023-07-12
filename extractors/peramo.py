from datetime import datetime, timezone, timedelta
import pytz
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from bs4 import NavigableString

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
        dates = re.search('(?P<date>\d{2}.\d{2}.\d{4})', tag, flags=re.IGNORECASE)
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
        a_tag = doc.find('a')
        if a_tag:
            href = self.__domain + a_tag['href']
            text = a_tag.string
            date_td = doc.select_one('td.views-field:has(span.date-display-single)')
            if date_td:
                date = self.__get_date(date_td.text)
            else:
                date = self.__get_date(text)
            return (text, date, href)
        else:
            return None

    def __extract_page(self, soup):
        doclist = []
        for doc in soup.select('table.views-table tr:has(td.views-field-uri)'):
            result = self.__extract_element(doc)
            if result:
                doclist.append(result)
        return doclist

    def __parse_contents(self, soup, caption):
        doclist = []
        doclist += self.__extract_page(soup)
        for page in soup.select('main.l-main ul.pagination.pager li:not(.first) a'):
            response = requests.get(self.__domain + page['href'], 
                                    headers=headers, verify=False)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            doclist += self.__extract_page(soup)
        if len(doclist) > 0:
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
        for menu_element in soup.select('aside.sidebar ul.menu \
                                    li.leaf a'):
            caption = menu_element.string
            response = requests.get(self.__domain + menu_element['href'], 
                                                headers=headers, verify=False)
            html = response.content
            soup = BeautifulSoup(html, 'html.parser')
            self.__parse_contents(soup, caption)
