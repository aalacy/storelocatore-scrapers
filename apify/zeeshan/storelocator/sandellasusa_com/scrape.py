import re 
import base 
from sgrequests import SgRequests

from lxml import (html, etree,)

from pdb import set_trace as bp

xpath = base.xpath

class Sandellasusa(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'sandellasusa.com'
    url = 'https://sandellasusa.com/locations'
    re_address = re.compile('([A-Z0-9]+) ([ \.A-Z0-9a-z]+) ([A-Z0-9a-z\.]+)')

    def map_data(self, row):

        # print('***********')
        # print(etree.tostring(row, pretty_print=True).decode("utf-8") )
        
        name = xpath(row, './/span//text()').strip().decode("utf-8") 
        
        text = etree.tostring(row).decode("utf-8") 
        text = re.sub('&#8217;|&nbsp;|&#160;', '', text)
        
        street_address = None
        street_address_matches = re.findall(self.re_address, text)
        if street_address_matches:
            street_address = ' '.join(street_address_matches[0])

        if not street_address:
            street_suny_match = re.match(r'Johnson Rd\. Commissary Bldg\.', text)
            if street_suny_match: 
                street_address = street_suny_match.group(0)

        if not street_address:
            street_rensselaer_match = re.match(r'15th and Sage Avenue', text)
            if street_rensselaer_match: 
                street_address = street_rensselaer_match.group(0)

        if not street_address:
            street_address = None        

        second_line = etree.tostring(row[1], pretty_print=True).decode("utf-8") 
        # if the second paragraph doesn't match the street address pattern 
            # and it's not equal to the value of street_address, then treat it as the first line of the address
        if not re.match(self.re_address, second_line):
            address_first_line = xpath(row[1], './/span//text()').strip().decode("utf-8") 
            # print(f'address_first_line: {address_first_line}')
            if street_address and street_address not in address_first_line:
                street_address = address_first_line + ' - ' + street_address
            else: 
                street_address = address_first_line

        city, state, zipcode = None, None, None
        region = re.findall(r'([A-Za-z]+)(,|) ([A-Z]+) ([0-9]+)', text)
        if region:
            city, _, state, zipcode = region[0]

        phone = re.findall(r'\d+-\d+-\d+', text)
        phone = phone[0] if phone else '<MISSING>'

        address = '%s, %s' % (street_address, region)
        geo = {} # self.get_geo(address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': name
            ,'street_address': street_address
            ,'city': city
            ,'state': state
            ,'zip': zipcode
            ,'country_code': self.default_country
            ,'store_number': '<MISSING>'
            ,'phone': phone
            ,'location_type': '<MISSING>'
            ,'naics_code': '<MISSING>'
            ,'latitude': geo.get('lat', '<MISSING>')
            ,'longitude': geo.get('lng', '<MISSING>')
            ,'hours_of_operation': '<MISSING>'
        }


    def crawl(self):
        session = SgRequests()
        session.session.headers.update({
            'authority': 'sandellasusa.com'
            ,'method': 'GET'
            ,'path': '/locations'
            ,'scheme': 'https'
            ,'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
            ,'accept-encoding': 'gzip, deflate, br'
            ,'accept-language': 'en-US,en;q=0.9,it;q=0.8'
            ,'cache-control': 'max-age=0'
            ,'upgrade-insecure-requests': '1'
            ,'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36)'
        })
        request = session.get(self.url)
        if request.status_code == 200:
            rows = html.fromstring(request.text).xpath('//div[@data-ux="ContentText"]')
            for row in rows:
                if xpath(row, './/span//text()') is None:
                    continue
                row_text = etree.tostring(row).decode("utf-8") 
                sub_rows = re.split('<p style=\"margin:0\"><span><br/></span></p>|<p style=\"margin:0\"><span>&#8203;</span></p>', row_text)

                if len(sub_rows) == 1: 
                    yield etree.fromstring(sub_rows[0])
                else:
                    for i, sub_row in enumerate(sub_rows):
                        if i == 0:
                            valid_html = sub_row + '</div>'
                        elif i == len(sub_rows)-1: 
                            valid_html = '<div>' + sub_row 
                        else:
                            valid_html = '<div>' + sub_row + '</div>'

                        el = etree.fromstring(valid_html)
                        if (len(el) > 0):
                            yield el


if __name__ == '__main__':
    s = Sandellasusa()
    s.run()
