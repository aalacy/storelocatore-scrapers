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

logger = SgLogSetup().get_logger("tesla_com__supercharger")


def fetch_data():
    ids = []
    url = "https://www.tesla.com/cua-api/tesla-locations?translate=en_US&usetrt=true"
    r = session.get(url, headers=headers)
    website = "tesla.com/supercharger"
    loc = "https://tesla.com/findus"
    logger.info("Pulling Stores")
    for item in json.loads(r.content):
        lid = item["location_id"]
        if "_" in lid:
            lid = lid.split("_")[0]
        ltype = item["location_type"]
        if "supercharger" in str(ltype):
            ids.append(lid)
    for lid in ids:
        logger.info(lid)
        lurl = "https://www.tesla.com/cua-api/tesla-location?translate=en_US&id=" + lid
        r2 = session.get(lurl, headers=headers)
        for line in r2.iter_lines():
            add = (
                line.split('"address_line_1":"')[1].split('"')[0]
                + " "
                + line.split('"address_line_2":"')[1].split('"')[0]
            )
            add = add.strip()
            name = line.split('"title":"')[1].split('"')[0]
            city = line.split('"city":"')[1].split('"')[0]
            state = line.split('"province_state":')[1].split(',"')[0].replace('"', "")
            zc = line.split('"postal_code":"')[1].split('"')[0]
            country = line.split('"country":"')[1].split('"')[0]
            lat = line.split('"latitude":"')[1].split('"')[0]
            lng = line.split('"longitude":"')[1].split('"')[0]
            store = lid
            typ = "Supercharger"
            hours = line.split('"hours":"')[1].split('"')[0]
            if hours == "":
                hours = "<MISSING>"
            if state == "" or state == "null":
                state = "<MISSING>"
            phone = line.split('"number":"')[1].split('"')[0].strip()
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
