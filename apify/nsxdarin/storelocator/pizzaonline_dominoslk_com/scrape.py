from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "api_key": "X24EZOH3IL",
}

logger = SgLogSetup().get_logger("pizzaonline_dominoslk_com")


def fetch_data():
    url = "https://apis.dominoslk.com/locator-service/ve2/cities?delivery_type=P"
    r = session.get(url, headers=headers)
    cities = []
    website = "pizzaonline.dominoslk.com"
    typ = "<MISSING>"
    country = "LK"
    logger.info("Pulling Stores")
    for item in json.loads(r.content)["data"]:
        if item != "TEST":
            cities.append(item)
    for cid in cities:
        logger.info(cid)
        curl = (
            "https://apis.dominoslk.com/locator-service/ve2/cities/" + cid + "/stores"
        )
        r2 = session.get(curl, headers=headers)
        for locitem in json.loads(r2.content)["data"]:
            store = locitem["id"]
            phone = locitem["phone"]
            name = locitem["name"]
            zc = "<MISSING>"
            lat = locitem["latitude"]
            lng = locitem["longitude"]
            city = locitem["city"]
            add = locitem["address"]
            state = locitem["region"]
            hours = "<MISSING>"
            loc = "https://m.dominoslk.com/changeAddress?redirectUrl=landing&deliveryType=D"
            rawadd = add
            add = add.replace("\r", "").replace("\n", "").replace("\t", "")
            if "ph no" in add:
                add = add.split("ph no")[0].strip()
            if "PH." in add:
                add = add.split("PH.")[0].strip()
            if "PH-" in add:
                add = add.split("PH-")[0].strip()
            if ", Sri Lanka" in add:
                add = add.split(", Sri Lanka")[0].strip()
            if ", SRI LANKA" in add:
                add = add.split(", SRI LANKA")[0].strip()
            if " Hotline" in add:
                add = add.split(" Hotline")[0].strip()
            if " Sri Lanka" in add:
                add = add.split(" Sri Lanka")[0].strip()
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
                raw_address=rawadd,
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
