import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('blueskycstores_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        r = requests.get('https://www.blueskycstores.com/locations')
        sel = html.fromstring(r.text)
        iframe_lnk = sel.xpath('//iframe/@data-src')[0]
        r = requests.get(iframe_lnk)
        sel = html.fromstring(r.text)
        script = sel.xpath('//script[contains(text(), "markerOpts")]/text()')[0]

        for st in script.split('var markerOpts = new Object();')[1:]:
            i = base.Item(sel)
            id_ = re.findall(r"markerOpts\['id'\] = (.+?);",st)
            if id_:
                i.add_value('store_number', id_[0])
            lat = re.findall(r"markerOpts\['markerLat'\] = (.+?);",st)
            if lat:
                i.add_value('latitude', lat[0])
            lng = re.findall(r"markerOpts\['markerLng'\] = (.+?);",st)
            if lng:
                i.add_value('longitude', lng[0])
            htm_ = re.findall(r"markerOpts\['bubbleHtml'\] = (.+?);",st)
            if htm_:
                htm = htm_[0].split('</p><p>')
                htm = [remove_tags(s.replace('\xa0','')) for s in htm]
                if len(htm) == 2:
                    htm.append('')
                i.add_value('location_name', htm[0], lambda x: x.replace('\'',''))
                i.add_value('phone', htm[1], lambda x: x.replace('\'',''))
                i.add_value('hours_of_operation', htm[2], lambda x: x.replace('\'',''), lambda x: x if x else '<MISSING>')
            i.add_value('locator_domain', 'https://www.blueskycstores.com/locations')
            i.add_value('page_url', 'https://www.blueskycstores.com/locations')
            yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
