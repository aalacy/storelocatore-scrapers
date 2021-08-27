from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("hiexpress_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    alllocs = []
    urls = [
        "https://www.ihg.com/holidayinnexpress/destinations/us/en/canada-hotels",
        "https://www.ihg.com/holidayinnexpress/destinations/us/en/united-states-hotels",
    ]
    for url in urls:
        states = []
        session = SgRequests()
        r = session.get(url, headers=headers)
        time.sleep(1)
        if r.encoding is None:
            r.encoding = "utf-8"
        for line in r.iter_lines(decode_unicode=True):
            if 'hotels"><span>' in line:
                states.append(line.split('href="')[1].split('"')[0])
        for state in states:
            cities = []
            logger.info("Pulling State %s..." % state)
            time.sleep(1)
            session = SgRequests()
            r2 = session.get(state, headers=headers)
            if r2.encoding is None:
                r2.encoding = "utf-8"
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'hotels"><span>' in line2:
                    cities.append(line2.split('href="')[1].split('"')[0])
            for city in cities:
                logger.info("Pulling City %s..." % city)
                time.sleep(1)
                session = SgRequests()
                r3 = session.get(city, headers=headers)
                if r3.encoding is None:
                    r3.encoding = "utf-8"
                for line3 in r3.iter_lines(decode_unicode=True):
                    if '"@type":"Hotel","name":"Holiday Inn Express' in line3:
                        lurl = line3.split('"url":"')[1].split('"')[0]
                        if lurl not in alllocs:
                            alllocs.append(lurl)
                            website = "hiexpress.com"
                            typ = "Hotel"
                            hours = "<MISSING>"
                            name = line3.split('"name":"')[1].split('"')[0]
                            add = line3.split('"streetAddress":"')[1].split('"')[0]
                            city = line3.split('"addressLocality":"')[1].split('"')[0]
                            try:
                                state = line3.split('"addressRegion":"')[1].split('"')[
                                    0
                                ]
                            except:
                                state = "<MISSING>"
                            zc = line3.split('"postalCode":"')[1].split('"')[0]
                            if "canada-hotels" in url:
                                country = "CA"
                            else:
                                country = "US"
                            try:
                                phone = line3.split('"telephone":"')[1].split('"')[0]
                            except:
                                phone = "<MISSING>"
                            lat = line3.split(',"latitude":')[1].split(",")[0]
                            lng = line3.split('"longitude":')[1].split("}")[0]
                            store = lurl.replace("/hoteldetail", "").rsplit("/", 1)[1]
                            yield SgRecord(
                                locator_domain=website,
                                page_url=lurl,
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
