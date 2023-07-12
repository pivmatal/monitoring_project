#!/home/ufk/ufk_venv/bin/python
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monitoring_project.settings")
django.setup()

from datetime import datetime, timezone
import pytz
localtime = pytz.timezone("Asia/Krasnoyarsk")

from monitoring.models import UK, PIF
from django.db.models import Q

import time

ogrn = '1021401047799'
file_name = 'otch.html'
extractor = 'wealthim'

pif = UK.objects.filter(uk_ogrn = ogrn).first()
pifset = PIF.objects.filter(Q(pif_uk = pif) & ~Q(pif_checkpage=''))

file_ = open(f'/home/ufk/monitoring_project/templates/{file_name}', 'w')

import importlib
module = importlib.import_module(f'extractors.{extractor}')
pifset = [1]
#module = importlib.import_module('extractors.wealthim')

url = 'https://www.wealthim.ru/about/disclosure/pif/opif/wimfa/documents/'

#ext = module.Extractor(url)
#ext.scrape()
#content = ext.get_data(180)
#print(content)

for pif in pifset:
    start_time = time.time()
    ext = module.Extractor(url)
    #ext = module.Extractor(pif.pif_checkpage)
    ext.scrape()
    content = ext.get_data(720)
    print(f'Execution time: {time.time() - start_time}')
    file_.write('<div class="container">')
#    file_.write('<h3>{}</h3><a href="{}">{}</a>'.format(pif.pif_shortname, pif.pif_checkpage, pif.pif_checkpage))
    for e in content:
        if len(e) > 0:
            file_.write('<h5>{}</h5>'.format(e[0]))
            for k in e[1]:
                if len(k) > 0:
                    file_.write('<div class="d-flex flex-wrap justify-content-between">')
                    file_.write('<a href=\"{}\">{}</a><p><b>{}</b>'.format(k[2], k[0], k[1]))
                    file_.write('</div>')
    file_.write('</div>')
file_.close()

