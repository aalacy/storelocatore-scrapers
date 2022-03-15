from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("sonicdrivein_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://locations.sonicdrivein.com/browse/"
    locs = []
    states = []
    cities = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="https://locations.sonicdrivein.com/' in line:
            states.append(line.split('<a href="')[1].split('"')[0])
    for state in states:
        logger.info("Pulling State %s..." % state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<a href="https://locations.sonicdrivein.com/' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        logger.info("Pulling City %s..." % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if "view details</a>" in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    for loc in locs:
        Found = True
        while Found:
            try:
                logger.info("Pulling Location %s..." % loc)
                url = loc
                add = ""
                city = ""
                state = ""
                zc = ""
                country = "US"
                phone = ""
                hours = ""
                lat = ""
                lng = ""
                store = ""
                name = "Sonic Drive-In"
                website = "sonicdrivein.com"
                typ = "Restaurant"
                r2 = session.get(loc, headers=headers)
                if r2.encoding is None:
                    r2.encoding = "utf-8"
                for line2 in r2.iter_lines(decode_unicode=True):
                    if '<div class="map-list-item-wrap" data-fid="' in line2:
                        store = line2.split(
                            '<div class="map-list-item-wrap" data-fid="'
                        )[1].split('"')[0]
                    if '"latitude": "' in line2:
                        lat = line2.split('"latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line2:
                        lng = line2.split('"longitude": "')[1].split('"')[0]
                    if '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0].strip()
                    if '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if '"addressRegion": "' in line2:
                        state = line2.split('"addressRegion": "')[1].split('"')[0]
                    if '"postalCode": "' in line2:
                        zc = line2.split('"postalCode": "')[1].split('"')[0]
                    if '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0].strip()
                    if '"openingHours": "' in line2:
                        hours = (
                            line2.split('"openingHours": "')[1].split('"')[0].strip()
                        )
                if hours == "":
                    hours = "<MISSING>"
                if phone == "":
                    phone = "<MISSING>"
                Found = False
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
            except:
                Found = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
