# -*- coding: cp1252 -*-
import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('greyhound_ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    r = session.get('https://www.greyhound.ca/en/locations/default.aspx', headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    VS = ''
    VSG = ''
    EV = ''
    for line in r.iter_lines(decode_unicode=True):
        if 'id="__VIEWSTATE" value="' in line:
            VS = line.split('id="__VIEWSTATE" value="')[1].split('"')[0]
        if 'id="__EVENTVALIDATION" value="' in line:
            EV = line.split('id="__EVENTVALIDATION" value="')[1].split('"')[0]
        if 'id="__VIEWSTATEGENERATOR" value="' in line:
            VSG = line.split('id="__VIEWSTATEGENERATOR" value="')[1].split('"')[0]
    url = 'https://www.greyhound.ca/en/locations/default.aspx'
    states = ['Ontario|ON','Alberta|AB','Colombie-Britannique|BC','Manitoba|MB','Nouveau-Brunswick|NB','Nouvelle-Écosse|NT','Nova Scotia|NS','Québec|PQ','Saskatchewan|SK','Territoire du Yukon|YT']
    for state in states:
        stabb = state.split('|')[1]
        stname = state.split('|')[0]
        payload = {'ctl00$ctl00$tkScptMngr': 'ctl00$ctl00$tkScptMngr|ctl00$ctl00$body$body$rcbState',
                   'ctl00_ctl00_tkScptMngr_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-CA:669ca791-a838-4419-82bc-9fa647338708:ea597d4b:b25378d2;Telerik.Web.UI:en-CA:8a61a1e3-95a3-45ac-933b-ed75a4bb0720:16e4e7cd:f7645509:22a6274a:ed16cbdc:24ee1bba:f46195d3:2003d0b8:c128760b:1e771326:88144a7a:aa288e2d:258f1c72:874f8ea2:19620875:92fe8ea0:fa31b949:4877f69a:490a9d4e:bd8f85e4;',
                   'ctl00$ctl00$body$body$txtZipCode': '',
                   'ctl00$ctl00$body$body$rcbState': stname,
                   'ctl00_ctl00_body_body_rcbState_ClientState': '{"logEntries":[],"value":"' + stabb + '","text":"' + stname + '","enabled":true,"checkedIndices":[],"checkedItemsTextOverflows":false}',
                   'ctl00$ctl00$body$body$rcbCity': 'select a city',
                   'ctl00_ctl00_body_body_rcbCity_ClientState': '',
                   'ctl00_ctl00_RadWindowManager_ClientState': '',
                   'ctl00_ctl00_RedirecttoGreyhoundRadWindow_ClientState': '',
                   'ctl00_ctl00_RadWindowManager2_ClientState': '',
                   'ioBlackBox': '',
                   '__EVENTTARGET': 'ctl00$ctl00$body$body$rcbState',
                   '__EVENTARGUMENT': '',
                   '__VIEWSTATE': VS,
                   '__VIEWSTATEGENERATOR': VSG,
                   '__EVENTVALIDATION': EV,
                   '__ASYNCPOST': 'true',
                   'RadAJAXControlID': 'ctl00_ctl00_tkAjxMngr'
                   }
        r = session.post(url, headers=headers, data=payload)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"value":"/en/locations/terminal.aspx?city=' in line:
                items = line.split('"value":"/en/locations/terminal.aspx?city=')
                for item in items:
                    if 'Telerik.Web.UI.RadComboBox' not in item:
                        lid = item.split('"')[0]
                        locs.append(lid + '|' + stabb)
    for loc in locs:
        lid = loc.split('|')[0]
        state = loc.split('|')[1]
        lurl = 'https://www.greyhound.ca/en/locations/terminal.aspx?city=' + lid
        store = lid
        logger.info(('Pulling Location %s...' % lurl))
        website = 'greyhound.ca'
        typ = '<MISSING>'
        phone = ''
        city = '<MISSING>'
        country = 'CA'
        zc = ''
        lat = ''
        lng = ''
        hours = ''
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        HFound = False
        for line2 in lines:
            if 'Station<' in line2:
                HFound = True
            if HFound and '</table>' in line2:
                HFound = False
            if HFound and '<td style="padding-right: 10px;">' in line2:
                g = next(lines)
                next(lines)
                next(lines)
                h = next(lines)
                hrs = g.strip().replace('\t','').replace('\r','').replace('\n','')
                hrs = hrs + ': ' + h.strip().replace('\t','').replace('\r','').replace('\n','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if 'Address' in line2:
                g = next(lines)
                h = next(lines)
                add = g.split('<')[0].strip().replace('\t','') + ' ' + h.split('<')[0].strip().replace('\t','')
                add = add.strip()
                g = ''
                while ',' not in g:
                    g = next(lines)
                city = g.split(',')[0].strip().replace('\t','')
                g = ''
                while '&nbsp;' not in g:
                    g = next(lines)
                state = g.split('&')[0].strip().replace('\t','')
                zc = g.split(';')[1].split('<')[0]
            if 'GetMap(' in line2:
                lat = line2.split('GetMap(')[1].split(',')[0].replace("'",'')
                lng = line2.split('GetMap(')[1].split(',')[1].replace("'",'')
            if '<h3>' in line2:
                name = line2.split('<h3>')[1].split('<')[0]
            if 'Call:' in line2:
                phone = line2.split('Call:')[1].split('<')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if state == 'PQ':
            state = 'QC'
##        city = name
##        if '(' in city:
##            city = city.split('(')[0].strip()
        if add == '':
            add = '<MISSING>'
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
