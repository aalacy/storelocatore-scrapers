from sgrequests import SgRequests
from sglogging import SgLogSetup
import json
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("ikea_com")


def fetch_data():
    url = "https://www.ikea.com/us/en/meta-data/navigation/stores-detailed.json"
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array:
        store = item["id"]
        loc = item["storePageUrl"]
        name = item["name"]
        add = item["address"]["street"]
        city = item["address"]["city"]
        state = item["address"]["stateProvinceCode"].replace("US", "")
        zc = item["address"]["zipCode"]
        phone = "1-888-888-4532"
        website = "ikea.com"
        typ = "Store"
        country = "US"
        hours = ""
        days = item["hours"]["normal"]
        for day in days:
            hrs = day["day"] + ": " + day["open"] + "-" + day["close"]
            if hours == "":
                hours = hrs
            else:
                hours = hours + "; " + hrs
        lat = item["lat"]
        lng = item["lng"]
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
