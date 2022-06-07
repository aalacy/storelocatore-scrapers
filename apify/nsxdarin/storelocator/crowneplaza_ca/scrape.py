from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("crowneplaza_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    alllocs = []
    urls = ["https://www.ihg.com/crowneplaza/destinations/us/en/canada-hotels"]
    for url in urls:
        states = []
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if (
                'href="https://www.ihg.com/crowneplaza/destinations/us/en/canada/'
                in line
            ):
                surl = line.split('href="')[1].split('"')[0]
                if surl not in states:
                    states.append(surl)
        for state in states:
            cities = []
            logger.info(("Pulling State %s..." % state))
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if (
                    'href="https://www.ihg.com/crowneplaza/destinations/us/en/canada/'
                    in line2
                    and "<span>" in line2
                ):
                    curl = line2.split('href="')[1].split('"')[0]
                    if curl not in cities:
                        cities.append(curl)
            for city in cities:
                logger.info(("Pulling City %s..." % city))
                r3 = session.get(city, headers=headers)
                for line3 in r3.iter_lines():
                    if (
                        "https://www.ihg.com/crowneplaza/hotels/" in line3
                        and '{"@context":"https://www.schema.org"' in line3
                    ):
                        lurl = line3.split('"url":"')[1].split('"')[0]
                        if lurl not in alllocs:
                            alllocs.append(lurl)
                            website = "crowneplaza.ca"
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
