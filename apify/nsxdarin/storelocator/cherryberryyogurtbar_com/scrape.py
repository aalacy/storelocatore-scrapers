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

logger = SgLogSetup().get_logger("cherryberryyogurtbar_com")


def fetch_data():
    for x in range(0, 10):
        url = "https://www.cherryberryyogurtbar.com/find-a-location?page=" + str(x)
        r = session.get(url, headers=headers)
        website = "cherryberryyogurtbar.com"
        typ = "<MISSING>"
        country = "US"
        loc = "https://www.cherryberryyogurtbar.com/find-a-location"
        name = "Cherry Berry"
        logger.info("Pulling Stores")
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode("utf-8"))
            if '<span itemprop="streetAddress">' in line:
                phone = "<MISSING>"
                city = ""
                state = ""
                zc = ""
                lat = ""
                lng = ""
                country = "US"
                add = (
                    line.split('<span itemprop="streetAddress">')[1]
                    .split("<")[0]
                    .strip()
                )
            if 'itemprop="addressLocality">' in line:
                city = line.split('itemprop="addressLocality">')[1].split("<")[0]
                state = line.split('addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line:
                zc = line.split('itemprop="postalCode">')[1].split("<")[0]
                store = "<MISSING>"
            if 'data-lat="' in line:
                lat = line.split('data-lat="')[1].split('"')[0]
                lng = line.split('long="')[1].split('"')[0]
            if '<a href="tel:' in line:
                phone = line.split('">')[1].split("<")[0]
            if (
                '<td  class="views-field views-field-field-catering' in line
                and 'scope="col">' not in line
            ):
                hours = "<MISSING>"
                if " " in zc:
                    country = "CA"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
