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

logger = SgLogSetup().get_logger("dominospizza_az")


def fetch_data():
    url = "https://server.dominospizza.az/api/dominos/stores/public"
    r = session.get(url, headers=headers)
    website = "dominospizza.az"
    typ = "<MISSING>"
    country = "AZ"
    state = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["data"]:
        name = item["storeName"]["en"]
        add = item["address"]["en"]
        store = item["_id"]
        hours = "Sun-Sat: " + str(item["openingHour"]) + "-" + str(item["closingHour"])
        phone = item["phone"]
        lat = str(item["location"]).split(",")[0].replace("[", "").strip()
        lng = str(item["location"]).split(",")[1].replace("]", "").strip()
        loc = "<MISSING>"
        zc = "<MISSING>"
        city = add.rsplit(",", 1)[1].strip()
        add = add.rsplit(",", 1)[0].strip()
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
