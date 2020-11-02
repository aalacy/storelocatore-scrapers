import re
from pprint import pprint
from string import capwords

import base
import requests, json
from urllib.parse import urljoin

from w3lib.html import remove_tags
from lxml import html
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('amestools_com')


crawled = []
class Scrape(base.Spider):

    def crawl(self):
        base_url = "https://amestools.com/store-locator/"
        raw_json = html.fromstring(requests.get(base_url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}).text).xpath('//script/text()[contains(., "maplistScriptParamsKo")]')[0]
        raw_json = re.findall(r'maplistScriptParamsKo = (\{.+?\});\n', raw_json)
        if raw_json:
            json_body = json.loads(raw_json[0])
            for result in json_body.get('KOObject', ["noting"])[0].get('locations', {}):
                i = base.Item(result)
                i.add_value('locator_domain', base_url)
                i.add_value('page_url', base_url)
                i.add_value('location_name', result.get('title',''), lambda x: x.strip())
                i.add_value('latitude', result.get('latitude', ''), lambda x: x.strip())
                i.add_value('longitude', result.get('longitude', ''), lambda x: x.strip())
                addr = result.get('address')
                if addr:
                    try:
                        if '<br />' in addr:
                            a = [s.strip() for s in addr.split('<br />') if s.strip()]
                            if len(a) == 2:
                                street = a[0]
                                loc = a[1].replace('\n', '')
                            elif len(a) == 3:
                                street = ', '.join(a[:2]).replace('\n','')
                                loc = a[2].replace('\n', '')
                            elif len(a) == 4:
                                street = ', '.join(a[:3]).replace('\n', '')
                                loc = a[3].replace('\n', '')
                        else:
                            street = addr.split('  ')[0]
                            loc = addr.split('  ')[1].replace('\n', '')
                        i.add_value('street_address', street, remove_tags, lambda x: x.strip())

                        st = re.findall(r'(.+?),\s([A-Z][A-Z])\s(.+?)<', loc)
                        if st:
                            i.add_value('city', st[0][0], lambda x: x.strip())
                            i.add_value('state', st[0][1], lambda x: x.strip())
                            i.add_value('zip', st[0][2], lambda x: x.strip())
                            i.add_value('country_code', base.get_country_by_code(i.as_dict()['state']), lambda x: x.strip())
                    except:
                        pass
                sub_html = html.fromstring(result['description'])
                i.add_value('phone', sub_html.xpath('//div[span[contains(text(), "Phone:")]]/text()'), base.get_first, lambda x: x.strip())
                i.add_value('location_type', result.get('categories', [])[0], lambda x: x['title'], lambda x: x.strip())
                hours = result['description'].split('<p><strong>Store Hours:</strong></p>')
                if len(hours) > 1:
                    text = [remove_tags(s).replace('\xa0', ' ') for s in hours[1].split('\n') if s]
                    i.add_value('hours_of_operation', '; '.join(text), lambda x: x.strip())

                yield i


if __name__ == '__main__':
    s = Scrape()
    s.run()
