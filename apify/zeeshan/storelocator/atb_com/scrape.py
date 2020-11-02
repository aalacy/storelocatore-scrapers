import re 
import base
import requests

from lxml import (html, etree,)

from pdb import set_trace as bp


xpath = base.xpath

class Atb(base.Base):

    csv_filename = 'data.csv'
    domain_name = 'atb.com'
    url = 'https://www.atb.com/_vti_bin/lists.asmx'

    def map_data(self, row):
        hours_of_operation = xpath(row, './/@ows_hours')
        clean_re = re.compile('<.*?>')
        hours_of_operation = re.sub(clean_re, '', hours_of_operation)

        street_address = xpath(row, './/@ows_address')
        street_address = street_address.replace('Physical location - ', '')
        street_address = street_address.replace('Physical Location - ', '')
        street_address = street_address.replace('<br>', '')
        street_address = street_address.replace('<br/>', '')
        street_address = street_address.replace('Mailing address - ', '')
        street_address = street_address.replace('Mailing Address - ', '')
        street_address = re.sub(r'<.*?>', '', street_address)
        street_address = re.sub(r'<.*?/>', '', street_address)

        return {
            'locator_domain': self.domain_name
            ,'location_name': xpath(row, './/@ows_title')
            ,'street_address': street_address
            ,'city': xpath(row, './/@ows_city')
            ,'state': 'Alberta'
            ,'zip': xpath(row, './/@ows_postal')
            ,'country_code': 'CA'
            ,'store_number': xpath(row, './/@ows_uniqueid')
            ,'phone': xpath(row, './/@ows_phone')
            ,'location_type': xpath(row, './/@ows_classification')
            ,'naics_code': None
            ,'latitude': xpath(row, './/@ows_lat')
            ,'longitude': xpath(row, './/@ows_long')
            ,'hours_of_operation': hours_of_operation
        }

    def crawl(self):
        session = requests.Session()
        session.headers.update({
            'Accept': 'application/xml, text/xml, */*; q=0.01'
            ,'Accept-Encoding': 'gzip, deflate, br'
            ,'Accept-Language': 'en-US,en;q=0.9,it;q=0.8'
            ,'Connection': 'keep-alive'
            ,'Content-Type': 'text/xml; charset="UTF-8"'
            ,'Host': 'www.atb.com'
            ,'Origin': 'https://www.atb.com'
            ,'Referer': 'https://www.atb.com/contact-us/Pages/branch-locator.aspx'
            ,'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
            ,'X-Requested-With': 'XMLHttpRequest'
        })
        payload = '''<soapenv:Envelope xmlns:soapenv='http://schemas.xmlsoap.org/soap/envelope/' xmlns:soap='http://schemas.microsoft.com/sharepoint/soap/'>        <soapenv:Body>          <GetListItems xmlns='http://schemas.microsoft.com/sharepoint/soap/'>                <listName>Branches</listName>                   <viewFields>                         <ViewFields>                           <FieldRef Name='ID' />                          <FieldRef Name='Title' />                           <FieldRef Name='Transit' />                             <FieldRef Name='Classification' />                          <FieldRef Name='Address' />                             <FieldRef Name='City' />                            <FieldRef Name='Postal' />                          <FieldRef Name='Phone' />                           <FieldRef Name='Fax' />                             <FieldRef Name='Hours' />                           <FieldRef Name='LAT' />                             <FieldRef Name='LONG' />                         </ViewFields>                     </viewFields>                     <rowLimit>0</rowLimit>                     <query>                         <Query>                             <OrderBy>                                   <FieldRef Name='Title' Ascending='True' />                              </OrderBy>                      </Query>                    </query>            </GetListItems>         </soapenv:Body>     </soapenv:Envelope>'''
        r = session.post(self.url, data=payload)
        if r.status_code == 200:
            hxt = html.fromstring(r.text)
            for store in hxt.xpath('//row'):
                yield store


if __name__ == '__main__':
    a = Atb()
    a.run()
