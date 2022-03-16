import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "hullsenvironmental.com"
LOCATION_URL = "https://www.hullsenvironmental.com/locations"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()

MISSING = "<MISSING>"


def fetch_data():
    soup = bs(session.get(LOCATION_URL, headers=HEADERS).content, "lxml")
    contents = soup.select(
        "section.locator-list div.lllb-wrap, div.llrb-wrap,div.llcb-wrap"
    )
    for row in contents:
        info = row.get_text(strip=True, separator="|").split("|")
        location_name = info[0].replace("\u200b", "").strip()
        street_address = info[1].strip()
        city_state_zip = info[2].split(",")
        city = city_state_zip[0].strip()
        state = re.sub(r"\d+", "", city_state_zip[1]).strip()
        zip_postal = re.sub(r"\D+", "", city_state_zip[1]).strip()
        country_code = "US"
        store_number = MISSING
        phone = info[4].replace("\u200b", "").strip()
        location_type = MISSING
        latitude = MISSING
        longitude = MISSING
        hours_of_operation = MISSING
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
            raw_address=f"{street_address}, {city}, {state} {zip_postal}",
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
