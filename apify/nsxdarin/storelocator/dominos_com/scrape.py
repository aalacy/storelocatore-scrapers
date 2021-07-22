from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_com")

letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']

searchurls = ['BRAZIL|https://order.golo01.dominos.com/store-locator-international/locate/store?regionCode=BR&latitude=-13.5415477&longitude=-56.3346976']

def fetch_data():
    for letter in letters:
        logger.info('Pulling Letter %s...' % letter)
        url = "https://www.dominos.nl/dynamicstoresearchapi/getlimitedstores/100/" + letter
        r = session.get(url, headers=headers)
        website = "dominos.com"
        typ = "<MISSING>"
        country = "<MISSING>"
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        logger.info("Pulling Stores")
        for item in json.loads(r.content)['Data']:
            name = item['Name']
            store = item['StoreNo']
            phone = item['PhoneNo']
            try:
                add = item['Address']['UnitNo'] + ' ' + item['Address']['StreetNo'] + ' ' + item['Address']['StreetName']
            except:
                add = "<MISSING>"
            city = item['Address']['Suburb']
            state = "<MISSING>"
            zc = item['Address']['PostalCode']
            lat = item['GeoCoordinates']['Latitude']
            lng = item['GeoCoordinates']['Longitude']
            hours = str(item['OpeningHours'])
            loc = "<MISSING>"
            country = item['CountryCode']
            yield SgRecord(
                locator_domain=website,
                page_url=loc,
                location_name=name,
                street_address=add,
                city=city,
                state=state,
                zip_postal=zc,
                country_code=country,
                phone=phone,
                location_type=typ,
                store_number=store,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hours,
            )

    for url in searchurls:
        lurl = url.split('|')[1]
        cc = url.split('|')[0]
        logger.info(lurl)
        headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'DPZ-Market': cc
            }
        r = session.get(lurl, headers=headers2)
        website = "dominos.br"
        typ = "<MISSING>"
        country = lurl.split('regionCode=')[1].split('&')[0]
        loc = "<MISSING>"
        store = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        logger.info("Pulling Stores")
        for item in json.loads(r.content)['Stores']:
            if 'StoreName' in str(item):
                name = item['StoreName']
                store = item['StoreID']
                phone = item['Phone']
                try:
                    add = item['StreetName']
                except:
                    add = "<MISSING>"
                add = str(add).replace('\r','').replace('\n','')
                city = str(item['City']).replace('\r','').replace('\n','')
                state = "<MISSING>"
                zc = item['PostalCode']
                try:
                    lat = item['StoreCoordinates']['StoreLatitude']
                    lng = item['StoreCoordinates']['StoreLongitude']
                except:
                    lat = "<MISSING>"
                    lng = "<MISSING>"
                hours = str(item['HoursDescription']).replace('\t','').replace('\n','').replace('\r','')
                loc = "<MISSING>"
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )

    locs = []
    states = []
    url = 'https://pizza.dominos.com/sitemap.xml'
    country = "US"
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'https://pizza.dominos.com/' in line and '/home/sitemap' not in line:
            states.append(line.replace('\r','').replace('\n','').replace('\t','').strip())
    for state in states:
        Found = True
        logger.info(('Pulling State %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'https://pizza.dominos.com/' in line2:
                if line2.count('/') == 4:
                    Found = False
                if Found:
                    locs.append(line2.replace('\r','').replace('\n','').replace('\t','').strip())
        logger.info(('%s Locations Found...' % str(len(locs))))
    for loc in locs:
        logger.info('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"branchCode":"' in line2:
                store = line2.split('"branchCode":"')[1].split('"')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                name = "Domino's #" + store
                website = 'dominos.com'
                country = 'US'
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                typ = 'Store'
                hours = line2.split('"openingHours":["')[1].split('"]')[0].replace('","','; ')
                try:
                    phone = line2.split(',"telephone":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=add,
                    city=city,
                    state=state,
                    zip_postal=zc,
                    country_code=country,
                    phone=phone,
                    location_type=typ,
                    store_number=store,
                    latitude=lat,
                    longitude=lng,
                    hours_of_operation=hours,
                )

def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        for rec in results:
            writer.write_row(rec)

scrape()
