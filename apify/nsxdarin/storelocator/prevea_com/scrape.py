import csv
import re
from sgrequests import SgRequests
from requests.utils import add_dict_to_cookiejar
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('prevea_com')




session = SgRequests()


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9,la;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Origin': 'https://www.prevea.com',
    'Referer': 'https://www.prevea.com/providers?loadmap=1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    'Upgrade-Insecure-Requests': '1'
}


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_crsf_token(html):
    regex = r"id=\"__CMSCsrfToken\" value=\"(.*?)\""
    match = re.search(regex, html)
    return match.group(1) if match else None


def get_view_state(html):
    regex = r"id=\"__VIEWSTATE\" value=\"(.*?)\""
    match = re.search(regex, html)
    return match.group(1) if match else None


def get_eastern_locations():
    url = 'https://www.prevea.com/providers?searchtype=location&zip=&newsearch=1'
    r = session.get(url, headers=headers)
    return r


def get_western_locations(csrf_token, view_state):

    post_data = {
        '__CMSCsrfToken': csrf_token,
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        'lng': 'en-US',
        '__VIEWSTATEGENERATOR': 'A5343185',
        '__SCROLLPOSITIONX': '0',
        '__SCROLLPOSITIONY': '0',
        'p$lt$widget1$ctl00$viewBiz$Region$list': 'West',
        'p$lt$widget2$ctl00$viewBiz$Region$list': 'East',
        'p$lt$WebPartZone8$searchZone$SmartSearchBox$txtWord': '',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$ProviderLocationSelectionRadio': 'Location',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$ProviderLocationKeywords': '',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$ProviderLocationMedicalService': '%23%23ALL%23%23',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$LocationZipCode': '',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$LocationMiles': '%23%23ALL%23%23',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$LocationType': '%23%23ALL%23%23',
        'p$lt$WebPartZone9$mainZone$pageplaceholder1$p$lt$WebPartZone5$LeftZone2$CustomProviderLocationSearch$LocationHealthCenterName': '',
        '__VIEWSTATE': view_state,
        'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '1',
        'p$lt$widget1$ctl00$viewBiz$btnOK': 'Submit',
    }

    headers['Content-Type']: 'application/x-www-form-urlencoded'

    add_cookies = {
        'CMSLandingPageLoaded': 'true',
        'CMSUserPage': '{"TimeStamp":"2020-06-25T05:10:04.6389331+00:00","LastPageDocumentID":95,"LastPageNodeID":97,"Identifier":"1fb590c0-4425-4170-9be3-0f0482f81f7e"}',
        'VisitorStatus': '11062144311',
        'btpdb.dcKDAzq.dGZjLjcwNDQxNTM': 'U0VTU0lPTg',
        'prism_799401111': '68b47a79-0677-417f-a7d4-6dcb75bcc9f3',
        'btpdb.dcKDAzq.dGZjLjc0MDY1NjQ': 'U0VTU0lPTg',
        'nmstat': '1593059832031',
        '_gcl_au': '1.1.1508404150.1593059756',
        '_ga': 'GA1.2.1683829215.1593059756',
        '_gid': 'GA1.2.1683829215.1593059756',
        '_fbp': 'fb.1.1593059756640.1874687172',
        '_gat_UA-901569-1': '1'
    }
    add_dict_to_cookiejar(session.get_session().cookies, add_cookies)

    url = 'https://www.prevea.com/providers?loadmap=1'
    r = session.post(url, headers=headers, data=post_data)
    r.raise_for_status()

    # remove content type header for subsequent GET requests for the detail pages
    headers.pop('Content-Type', None)

    return r


def parse_locations(response, locs):
    for line in response.iter_lines(decode_unicode=True):
        if '<strong><a href=\\"/locations' in line:
            loc = 'https://www.prevea.com/locations' + line.split('<strong><a href=\\"/locations')[1].split('\\')[0]
            locs.append(loc)


def fetch_data():
    locs = []

    r = get_eastern_locations()
    parse_locations(r, locs)

    csrf_token = get_crsf_token(r.text)
    view_state = get_view_state(r.text)
    r = get_western_locations(csrf_token, view_state)
    parse_locations(r, locs)

    # logger.info('locs', locs)

    for loc in locs:
        # logger.info('Pulling Location %s...' % loc)
        website = 'prevea.com'
        typ = ''
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = '<MISSING>'
        phone = ''
        lat = ''
        lng = ''
        Found = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"@context": "' in line2:
                Found = True
            if Found and ',"isAcceptingNewPatients":' in line2:
                Found = False
            if Found and '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0]
            if Found and '"name": "' in line2:
                name = line2.split('"name": "')[1].split('"')[0]
            if Found and '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0]
            if Found and '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if Found and '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if Found and '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if Found and '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if Found and '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '<h4><em><strong>' in line2:
                tname = line2.split('<h4><em><strong>')[1].split('<')[0]
                if typ == '':
                    typ = tname
                else:
                    typ = typ + ', ' + tname
        if hours == '':
            hours = '<MISSING>'
        if typ == '':
            typ = '<MISSING>'
        if ', Suite' in add:
            add = add.split(', Suite')[0]
        if ', Inside' in add:
            add = add.split(', Inside')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
