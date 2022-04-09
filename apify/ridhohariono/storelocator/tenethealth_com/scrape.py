from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json


DOMAIN = "tenethealth.com"
LOCATION_URL = "https://www.tenethealth.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_location_type(dic):
    try:
        return next(iter(dic.values()))["Title"].strip()
    except StopIteration:
        return


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find(
        "script", string=re.compile(r"var simplemaps_usmap_mapdata")
    ).string
    data = json.loads(
        re.sub(
            r"([\{\s,])(\w+)(:)",
            r'\1"\2"\3',
            re.search(r"locations:(.*),\n?.*labels:", contents)
            .group(1)
            .replace("F:", "")
            .replace("P:", "PHONE")
            .replace("Rehabilitation:", "Rehabilitation - "),
        )
    )
    for key, val in data.items():
        page_url = val["detailurl"]
        location_name = val["name"]
        street_address = val["address"].strip().rstrip(",")
        if "http" in street_address:
            street_address = MISSING
        state = val["state"]
        city = re.sub(r"Suite\s.+,|\s" + state, "", val["city"]).strip().rstrip(",")
        zip_postal = val["zip"]
        country_code = "US"
        phone = (
            val["phone"]
            .replace(
                "Imaging/Radiology (includes Mammography and Bone Densitometry):", ""
            )
            .replace("PHONE", "")
            .replace("Scheduling", "")
            .split(",")[0]
            .split("& Rehabilitation -")[0]
            .split("x")[0]
            .split("/")[0]
            .split("|")[0]
        )
        location_type = get_location_type(val["facilitytypes"])
        store_number = key
        hours_of_operation = "<INACCESSIBLE>"
        latitude = val["lat"]
        longitude = val["lng"]
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
