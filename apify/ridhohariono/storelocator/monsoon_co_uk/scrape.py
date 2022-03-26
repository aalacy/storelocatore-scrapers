import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import json

DOMAIN = "monsoon.co.uk"
BASE_URL = "https://www.monsoon.co.uk"
LOCATION_URL = "https://www.monsoon.co.uk/stores/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()

MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_hours(hour_content):
    hoo = []
    for day in hour_content:
        if "isClosed" in hour_content[day]:
            hoo.append(day + ": CLOSED")
        else:
            start = str(hour_content[day]["openIntervals"][0]["start"])
            end = str(hour_content[day]["openIntervals"][0]["end"])
            hours = "{}:{} - {}:{}".format(start[:2], start[-2:], end[:2], end[-2:])
            hoo.append(day + ": " + hours)
    return ", ".join(hoo)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    stores = soup.find("div", {"data-component": "global/Tabs"}).find_all(
        "div", {"data-component": "stores/storeDetails"}
    )
    for row in stores:
        content = row.find("div", {"class": "b-store-card"})
        info = json.loads(row["data-component-store"])
        location_name = info["name"]
        if info["address2"] and len(info["address2"]) > 0:
            street_address = "{}, {}".format(info["address1"], info["address2"])
        else:
            street_address = info["address1"]
        city = info["city"]
        state = MISSING
        zip_postal = info["postalCode"]
        country_code = "GB"
        phone = MISSING if "phone" not in info else info["phone"]
        hours_of_operation = (
            content.find("div", {"class": "b-store-card__hours"})
            .get_text(strip=True, separator=",")
            .replace("Opening hours:,", "")
            .replace(",Holiday hours:", "")
            .replace(":,", ": ")
        )
        sub_hoo = re.sub(r"[a-z]*:\s+", "", hours_of_operation, flags=re.IGNORECASE)
        if all(value == "CLOSED" for value in sub_hoo.split(",")):
            location_type = "TEMP_CLOSED"
        else:
            location_type = "OPEN"
        store_number = info["ID"]
        latitude = info["latitude"]
        longitude = info["longitude"]
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
            raw_address=f"{street_address}, {city}, {zip_postal}".strip(),
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
