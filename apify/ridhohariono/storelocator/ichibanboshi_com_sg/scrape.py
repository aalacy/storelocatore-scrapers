from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json

DOMAIN = "ichibanboshi.com.sg"
LOCATION_URL = "https://www.ichibanboshi.com.sg/en/?section=15"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    content = soup.find("script", string=re.compile(r"markers:.*"))
    data = json.loads(
        re.search(r"markers:(.*) }\); var", " ".join(content.string.split()))
        .group(1)
        .replace("}, ]", "}]")
        .replace('", }', '"}')
    )["data"]
    for row in data:
        location_name = re.sub(r"\(Closed.*\)", "", row["title"])
        street_address = row["address2"]
        city_zip = row["address3"].split(" ")
        city = city_zip[0].strip()
        state = MISSING
        zip_postal = city_zip[1].strip()
        phone = row["tel"]
        country_code = "SG"
        hours_of_operation = (
            " ".join(
                (
                    re.sub(r"\(.*\)|\(.*pm", "", row["misc2"])
                    + ","
                    + re.sub(r"\(.*\)|\(.*pm", "", row["misc3"])
                ).split()
            )
            .replace("/", ",")
            .rstrip(",")
        )
        store_number = MISSING
        location_type = row["misc1"].replace("Store Specialty: ", "").strip()
        latitude = row["lat"]
        longitude = row["lng"]
        log.info("Append {} => {}, {}".format(location_name, street_address, city))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
