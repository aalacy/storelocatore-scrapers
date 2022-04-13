from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
import re

DOMAIN = "mammaroma.be"
BASE_URL = "https://mammaroma.be"
LOCATION_URL = "https://mammaroma.be/restaurants/"
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
    contents = soup.select("div.edgtf-elements-holder-item-inner")
    for row in contents:
        info = re.sub(
            r"@@?Email.*", "", row.get_text(strip=True, separator="@@")
        ).split("@@")
        if not info or len(info) == 1:
            continue
        location_name = " ".join(info[:2]).strip()
        raw_address = ", ".join(info[2:4]).strip()
        addr_split = raw_address.split(",")
        street_address = addr_split[0].strip()
        state = MISSING
        city = addr_split[1].strip().split(" ")[1].strip()
        zip_postal = addr_split[1].strip().split(" ")[0].strip()
        country_code = "BE"
        hoo_phone = info[4:]
        store_number = MISSING
        if "Tel:" not in hoo_phone:
            phone = MISSING
            hours_of_operation = ", ".join(hoo_phone[1:]).strip()
        else:
            phone = hoo_phone[-1]
            hours_of_operation = ", ".join(hoo_phone[1:-2]).strip()
        location_type = MISSING
        if "Fermé temporairement" in hoo_phone:
            location_type = "TEMP_CLOSED"
        latitude = MISSING
        longitude = MISSING
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
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
