from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import SgLogSetup
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("sallybeauty_co_uk")


def fetch_data():
    url = "https://www.sallybeauty.co.uk/on/demandware.store/Sites-sally-beauty-Site/en_GB/Stores-GetStoresJSON"
    r = session.get(url, headers=headers)
    website = "sallybeauty.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["ID"]
        state = "<MISSING>"
        name = item["name"]
        add = item["address"]
        phone = item["phone"]
        city = item["city"]
        zc = item["postalCode"]
        lat = item["latitude"]
        lng = item["longitude"]
        hours = item["hours"]
        loc = "https://www.sallybeauty.co.uk/storeinfo?StoreID=" + store
        if phone == "" or phone is None:
            phone = "<MISSING>"
        if hours == "" or hours is None:
            hours = "<MISSING>"
        addinfo = item["formattedAddress"]
        if addinfo.count(",") == 4:
            add = addinfo.split(",")[0] + " " + addinfo.split(",")[1]
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
