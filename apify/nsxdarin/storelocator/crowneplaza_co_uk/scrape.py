from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("crowneplaza_co_uk")


def fetch_data():
    locs = []
    url = "https://www.ihg.com/bin/sitemap.crowneplaza.en-gb.hoteldetail.xml"
    r = session.get(url, headers=headers)
    website = "crowneplaza.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            'href="https://www.ihg.com/crowneplaza/hotels/gb/en/' in line
            and "hoteldetail" in line
        ):
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        Retry = True
        rc = 0
        while Retry and rc <= 5:
            Retry = False
            rc = rc + 1
            try:
                logger.info(loc)
                name = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
                phone = ""
                lat = ""
                lng = ""
                GB = False
                hours = "<MISSING>"
                r2 = session.get(loc, headers=headers)
                for line2 in r2.iter_lines():
                    if '"addressCountry": "United Kingdom"' in line2:
                        GB = True
                    if '"og:title" content="' in line2:
                        name = line2.split('"og:title" content="')[1].split('"')[0]
                    if '"latitude": "' in line2:
                        lat = line2.split('"latitude": "')[1].split('"')[0]
                    if '"longitude": "' in line2:
                        lng = line2.split('"longitude": "')[1].split('"')[0]
                    if '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0]
                    if '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if '"postalCode": "' in line2:
                        zc = line2.split('"postalCode": "')[1].split('"')[0]
                    if '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                if GB is True:
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
                Retry = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
