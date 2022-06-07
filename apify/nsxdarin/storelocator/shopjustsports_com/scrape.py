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

logger = SgLogSetup().get_logger("shopjustsports_com")


def fetch_data():
    url = "https://stockist.co/api/v1/u12231/locations/all"
    r = session.get(url, headers=headers)
    website = "shopjustsports.com"
    typ = "<MISSING>"
    country = "US"
    lurl = "https://www.shopjustsports.com/pages/stores"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["id"]
        name = item["name"]
        lat = item["latitude"]
        lng = item["longitude"]
        add = item["address_line_1"]
        city = item["city"]
        state = item["state"]
        zc = item["postal_code"]
        phone = item["phone"]
        hours = str(item["description"])
        hours = (
            hours.replace("STORE HOURS\n", "")
            .replace("\t", "")
            .replace("\r", "")
            .replace("\n", "; ")
        )
        if "; ;" in hours:
            hours = hours.split("; ;")[0]
        hours = hours.strip()
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
