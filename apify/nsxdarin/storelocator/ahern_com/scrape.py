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

logger = SgLogSetup().get_logger("ahern_com")


def fetch_data():
    url = "https://www.ahern.com/themes/theaherns/js/plugins/storeLocator/data/locations.json?formattedAddress=&boundsNorthEast=&boundsSouthWest="
    r = session.get(url, headers=headers)
    website = "ahern.com"
    typ = "<MISSING>"
    loc = "https://www.ahern.com/locations"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["location"]
        name = item["name"]
        lat = item["lat"]
        lng = item["lng"]
        add = item["address"]
        city = item["city"]
        state = item["state"]
        zc = item["postal"]
        phone = item["phone"]
        hours = item["hours1"] + "; " + item["hours2"] + "; " + item["hours3"]
        hours = (
            hours.strip()
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("  ", " ")
            .replace("\t", "")
        )
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
