from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import re

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
        try:
            logger.info(lid)
            lurl = (
                "https://www.tesla.com/cua-api/tesla-location?translate=en_US&id=" + lid
            )
            r2 = session.get(lurl, headers=headers)
            js = json.loads(r2.text)
            add = js["address_line_1"] + " " + js["address_line_2"]
            add = add.strip()
            name = js["title"]
            city = js["city"]
            state = js["province_state"]
            zc = js["postal_code"]
            country = js["country"]
            lat = js["latitude"]
            lng = js["longitude"]
            store = lid
            typ = "Supercharger"
            hours = js["hours"]
            if state == "" or state == "null":
                state = "<MISSING>"
            phonestr = str(js["sales_phone"])
            try:
                phone = phonestr.split("'number': '")[1].split("'")[0].strip()
            except:
                phone = "<MISSING>"
            clean = re.compile("<.*?>")
            hours = (
                re.sub(clean, "", hours)
                .replace("\n", ";")
                .replace("\\n", ";")
                .replace("\\t", "")
                .replace("\t", "")
                .replace("\\r", ";")
                .replace("\r", ";")
            )
            hours = hours.replace(";;", ";").replace(";;", ";")
            if "Store Hours;" in hours:
                hours = hours.split("Store Hours;")[1]
            if ";Service" in hours:
                hours = hours.split(";Service")[0]
            hours = hours.replace("Supercharger Hours", "")
            if "/" in phone:
                phone = phone.split("/")[0].strip()
            phone = (
                phone.replace("</p>", "")
                .replace("\\r", "")
                .replace("\r", "")
                .replace("\\n", "")
                .replace("\n", "")
            )
            add = (
                add.replace("\\n", "")
                .replace("\\r", "")
                .replace("\n", "")
                .replace("\r", "")
            )
            if "San Fran" in zc:
                zc = "94129"
                city = "San Francisco"
            if ";Sche" in hours:
                hours = hours.split(";Sche")[0].strip()
            if ";Sales Hours" in hours:
                hours = hours.split(";Sales Hours")[1].strip()
            if "null" in hours:
                hours = "<MISSING>"
            hours = (
                hours.replace("0S", "0; S")
                .replace("0T", "0; T")
                .replace("0F", "0; F")
                .replace("0M", "0; M")
                .replace("0W", "0; W")
            )
            if "Service Hours" in hours:
                hours = hours.split("Service Hours")[0].strip()
            if "0" not in hours:
                hours = "<MISSING>"
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
