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

logger = SgLogSetup().get_logger("kirbyfoodsiga_com")


def fetch_data():
    url = "https://api.freshop.com/1/stores?app_key=kirby_foods_iga&has_address=true&limit=-1&token=f7cdac7645a3ef3e545737dae99758de"
    r = session.get(url, headers=headers)
    website = "kirbyfoodsiga.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["items"]:
        store = item["id"]
        lat = item["latitude"]
        lng = item["longitude"]
        name = item["name"]
        loc = item["url"]
        add = item["address_1"]
        city = item["city"]
        state = item["state"]
        zc = item["postal_code"]
        hours = item["hours_md"]
        phone = item["phone"]
        phone = str(phone)
        phone = (
            phone.replace("\n", "").replace("\r", "").replace("\t", "").replace("*", "")
        )
        hours = str(hours)
        hours = (
            hours.replace("\n", "").replace("\r", "").replace("\t", "").replace("*", "")
        )
        if "Pharmacy" in hours:
            hours = hours.split("Pharmacy")[0].strip()
        if "Fax" in phone:
            phone = phone.split("Fax")[0].strip()
        if "Pharmacy" in phone:
            phone = phone.split("Pharmacy")[0].strip()
        phone = phone.replace("Store: ", "")
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
