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

logger = SgLogSetup().get_logger("dominos_com_sg")


def fetch_data():
    url = "https://api.dominos.com.sg/api/Stores?State=EA"
    r = session.get(url, headers=headers)
    website = "dominos.com.sg"
    typ = "<MISSING>"
    country = "SG"
    loc = "<MISSING>"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        store = item["Id"]
        name = item["Name"]
        lat = item["Latitude"]
        lng = item["Longitude"]
        hours = item["BusinessHours"]
        add = item["Address"]
        city = "Singapore"
        zc = add.strip().rsplit(" ", 1)[1]
        state = "<MISSING>"
        add = add.split("Singapore")[0].strip()
        phone = "<MISSING>"
        add = (
            add.replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace("\\r", "")
            .replace("\\n", "")
        )
        if "Test" not in name and "Test" not in add:
            add = add.replace(",", "").strip().replace("  ", " ")
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
