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

logger = SgLogSetup().get_logger("dominos_vn")


def fetch_data():
    url = "https://dominos.vn/api/v1/stores?main-store=false&store-filter.province-id=&type=1"
    r = session.get(url, headers=headers)
    website = "dominos.vn"
    typ = "<MISSING>"
    country = "VN"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["data"]:
        store = item["id"]
        name = item["name"]
        add = item["address_en"]
        city = name.rsplit("-", 1)[1].strip()
        state = "<MISSING>"
        zc = "<MISSING>"
        lat = item["lat"]
        lng = item["lon"]
        phone = "<MISSING>"
        ope = str(item["open_time"]).split("T")[1].rsplit(":", 1)[0]
        clo = str(item["close_time"]).split("T")[1].rsplit(":", 1)[0]
        hours = "Sun-Sat: " + ope + "-" + clo
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
