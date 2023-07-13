#!/home/ufk/ufk_venv/bin/python
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import django
import os

import send_to_email_avaliable
import create_screen

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoring_project.settings")
django.setup()

from datetime import datetime, timezone
import pytz
localtime = pytz.timezone("Asia/Krasnoyarsk")

from fake_useragent import UserAgent
fua = UserAgent(verify_ssl=False)

from monitoring.models import UK, MonitoringLog, PUCB

active_uks = UK.objects.filter(uk_enabled=True)

#headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
headers = {'User-Agent': fua.random}
timeout = 5

notavailable = []
notavailable_site_two_hour = []
available = []
errors = []

monlog = MonitoringLog(status="Started")
monlog.save()

file_path_one = 'image_one_hour' #скрин с сайтом который не доступен 1 час
file_path_two = 'image_two_hour' #скрин с сайтом который не доступен 2 часа
for f in os.listdir(file_path_one): # здесь мы чистим директории перед тем как что-то туда сохрагнить
    os.remove(os.path.join(file_path_one, f))

for f in os.listdir(file_path_two):
    os.remove(os.path.join(file_path_two, f))

for uk in active_uks:
    site = uk.uk_sitetype.strip() + "://" + uk.uk_site
    print("Doing: {}    {}    {}      {}".format(uk.uk_npp, site, uk.uk_sitetype.strip(), uk.uk_site))
    try:
        s = requests.Session()
        if uk.uk_sitetype == "https":
            response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers, verify=False)
        else:
            response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers)

    except requests.exceptions.SSLError as se:
        uk.save()
        pass
    except requests.exceptions.RequestException as re:
        retries = 4
        response = None
        for retry in range(retries):
            print("Retrying {}...".format(retry + 1))
            try:
                if uk.uk_sitetype == "https":
                    response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers, verify=False)
                else:
                    response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers)
            except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as err:
                pass
            else:
                break
        if response is not None and response.status_code == 200:
            uk.site_unavailable_code = 0
            uk.site_error_text = ''
            uk.save()
        else:
            timedelta = datetime.now(timezone.utc) - uk.uk_lastaccess
            if (timedelta.seconds // 3600) >=1:
               notavailable.append([uk.uk_shortname, site, str(re)])
            elif (timedelta.seconds // 3600) >=2:
                notavailable_site_two_hour.append([uk.uk_shortname, site, str(re)])
            else:
                errors.append([uk.uk_shortname, site, str(re)])
            if response is not None:
                uk.site_unavailable_code = response.status_code
            uk.site_error_text = str(re)
    else:
        if response.status_code == 200:
            uk.site_unavailable_code = 0
            uk.site_error_text = ''
            timedelta_available = datetime.now(timezone.utc) - uk.uk_lastaccess
            if(timedelta_available.seconds // 3600) >=1:
                print("Сайт {} снова доступен после более часа недоступности.".format(site))
                available.append(site)
            uk.save()
        else:
            response = s.get(site, allow_redirects=True, timeout=timeout, headers=headers)
            if response.status_code == 200:
                uk.site_unavailable_code = 0
                uk.site_error_text = ''
                timedelta_available = datetime.now(timezone.utc) - uk.uk_lastaccess
                if(timedelta_available.seconds // 3600) >=1:
                    print("Сайт {} снова доступен после более часа недоступности.".format(site))
                    available.append(site)
                uk.save()
            else:
                uk.site_unavailable_code = response.status_code

        timedelta = datetime.now(timezone.utc) - uk.uk_lastaccess
        if (timedelta.seconds // 3600) >=1:
           notavailable.append([uk.uk_shortname, site, response.status_code])
        if (timedelta.seconds // 3600) >=2:
           notavailable_site_two_hour.append([uk.uk_shortname, site, response.status_code])

active_pucb = PUCB.objects.filter(pucb_enabled=True)
for pucb in active_pucb:
    site = pucb.pucb_sitetype.strip() + "://" + pucb.pucb_site
    print("Doing: {}    {}    {}      {}".format(pucb.pucb_npp, site, pucb.pucb_sitetype.strip(), pucb.pucb_site))
    try:
        s = requests.Session()
        if pucb.pucb_sitetype == "https":
            response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers, verify=False)
        else:
            response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers)

    except requests.exceptions.SSLError as se:
        pucb.save()
        pass
    except requests.exceptions.RequestException as re:
        retries = 4
        response = None
        for retry in range(retries):
            print("Retrying {}...".format(retry + 1))
            try:
                if pucb.pucb_sitetype == "https":
                    response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers, verify=False)
                else:
                    response = s.head(site, allow_redirects=True, timeout=timeout, headers=headers)
            except (requests.exceptions.ReadTimeout, requests.exceptions.RequestException) as err:
                pass
            else:
                break
        if response is not None and response.status_code == 200:
            uk.save()
        else:
            timedelta = datetime.now(timezone.utc) - pucb.pucb_lastaccess

            if (timedelta.seconds // 3600) >=1:
               notavailable.append([pucb.pucb_name, site, str(re)])
            elif (timedelta.seconds // 3600) >=2:
               notavailable_site_two_hour.append([pucb.pucb_name, site, str(re)])
            else:
                errors.append([pucb.pucb_name, site, str(re)])
            #if response is not None:
            #    uk.site_unavailable_code = response.status_code
            #uk.site_error_text = str(re)
    else:
        if response.status_code == 200:
            timedelta_available = datetime.now(timezone.utc) - uk.uk_lastaccess
            if(timedelta_available.seconds // 3600) >=1:
                print("Сайт {} снова доступен после более часа недоступности.".format(site))
                available.append(site)
            pucb.save()
        else:
            response = s.get(site, allow_redirects=True, timeout=timeout, headers=headers)
            if response.status_code == 200:
                timedelta_available = datetime.now(timezone.utc) - uk.uk_lastaccess
                if(timedelta_available.seconds // 3600) >=1: # до сохранения данных, мы проверяем что сайт доступен(код 200) и проверяем последннее время доступности
                    print("Сайт {} снова доступен после более часа недоступности.".format(site))
                    available.append(site)
                pucb.save()
                
        timedelta = datetime.now(timezone.utc) - uk.uk_lastaccess

        if (timedelta.seconds // 3600) >=1:
           notavailable.append([pucb.pucb_name, site, response.status_code])
        if (timedelta.seconds // 3600) >=2:
           notavailable_site_two_hour.append([pucb.pucb_name, site, response.status_code])


print(available)

if len(notavailable) > 0:
    create_screen.create_screen(notavailable,'image_one_hour')

if len(notavailable_site_two_hour) > 0:
    create_screen.create_screen(notavailable_site_two_hour,'image_two_hour')

if len(available) > 0: 
    send_to_email_avaliable.send_email_about_avaliable(available)


monlog.status = "Ended"
monlog.date = datetime.now()
monlog.unavailable = len(notavailable)
monlog.errors = len(errors) 
monlog.save()

monstatus = open("./templates/monstatus.html", "w")

monstatus.write("<table class='table'>\n<thead>\n<tr>\n")
monstatus.write("<th scope='col'>Название</th>\n")
monstatus.write("<th scope='col'>Ссылка</th>\n")
monstatus.write("<th scope='col'>Ошибка</th>\n")
monstatus.write("</thead>\n</tr>\n")

monstatus.write("<tbody>\n")
if len(notavailable) > 0:
    for site in notavailable:
        monstatus.write("<tr>\n")
        monstatus.write("<td>{}</td>\n".format(site[0]))
        monstatus.write("<td><a href='{}'>{}</a></td>\n".format(site[1], site[1]))
        monstatus.write("<td>{}</td>\n".format(site[2]))
        monstatus.write("</tr>\n")

if len(errors) > 0:
    for site in errors:
        monstatus.write("<tr>\n")
        monstatus.write("<td>{}</td>\n".format(site[0]))
        monstatus.write("<td><a href='{}'>{}</a></td>\n".format(site[1], site[1]))
        monstatus.write("<td>{}</td>\n".format(site[2]))
        monstatus.write("</tr>\n")
monstatus.write("</tbody>\n")
monstatus.write("</table>\n")

monstatus.close()




