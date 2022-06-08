from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
import json


DOMAIN = "staples.se"
BASE_URL = "https://www.staples.se/"
LOCATION_URL = "https://www.staples.se/store-finder"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    data = json.loads(
        re.sub(
            r'(")(\d{2})(")',
            r"\2",
            re.sub(
                r"([\{\s,])(\w+)(:)",
                r'\1"\2"\3',
                soup.find("script", string=re.compile(r"stores\s=\s"))
                .string.replace("];", "]")
                .replace("stores = ", ""),
            ),
        ).replace("'", '"')
    )
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for row in data:
        location_name = row["addName"].strip()
        street_address = (
            row["addLine1"] + " " + row["addLine2"] + " " + row["addLine3"]
        ).strip()
        city = row["city"]
        state = row["state"] or MISSING
        zip_postal = row["postalCode"] or MISSING
        phone = row["phoneMobile"]
        country_code = "SE" if row["country"] == "Sverige" else row["country"]
        hoo = ""
        for day in days:
            hour = row["info" + day]
            if hour == "Stengt" or hour == "Stängt":
                hour = "Closed"
            hoo += day.title() + ": " + hour + ", ".strip()
        hours_of_operation = hoo.strip().rstrip(",")
        location_type = MISSING
        store_number = row["storeid"]
        latitude = row["latitude"]
        longitude = row["longitude"]
        log.info("Append {} => {}".format(location_name, street_address))
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
