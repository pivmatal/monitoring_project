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
        
    def __extract_element(self, doc, date_td_id):
        a_tag = doc.find('a')
        if a_tag is not None:
            href = self.__domain + a_tag['href']
            tds = doc.select('td')
            text = tds[0].text
            if date_td_id != -1:
                date = self.__get_date(tds[date_td_id].text)
            else:
                date_tds = [td for td in tds[1:] if re.match('\d{2}.\d{2}.\d{4}', td.text)]
                if len(date_tds) > 0:
                    date = self.__get_date(date_tds[0].text)
                else:
                    date = self.__get_date(text)
            return (text, date, href)
        else:
            return None

    def __parse_contents(self, soup):
        sections = soup.select('div.vkladki.PIF span')
        for section in sections:
            caption = section.string
            doclist = []
            for table in soup.select(f'div.{section["id"]} table'):
                headers = table.select('tr th')
                date_headers = [idth for idth, th in enumerate(headers) if re.search('(раскр|публик)', th.text)]
                if len(date_headers) > 0:
                    date_td_id = date_headers[0]
                else:
                    date_td_id = -1
                for row in table.select('tr:has(a)'):
                    result = self.__extract_element(row, date_td_id)
                    if result is not None:
                        doclist.append(result)
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
        self.__parse_contents(soup)
