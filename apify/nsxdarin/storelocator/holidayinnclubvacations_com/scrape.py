from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("holidayinnclubvacations_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.ihg.com/ubeapi/holidayinnclubvacations/cv/us/en/explore.json"
    r = session.get(url, headers=headers)
    website = "holidayinnclubvacations.com"
    country = "US"
    hours = "<MISSING>"
    for item in json.loads(r.content)["markers"]:
        add = item["address"]
        city = item["city"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["hotelName"]
        store = item["hotelCode"]
        typ = item["brand"]
        loc = "https:" + item["url"]
        zc = ""
        phone = ""
        state = ""
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        for line in r2.iter_lines():
            if '"addressRegion": "' in line:
                state = line.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line:
                zc = line.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line:
                phone = line.split('"telephone": "')[1].split('"')[0]
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
