from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "nenechicken.com.sg"
LOCATION_URL = "http://www.nenechicken.com.sg/store-locations/"
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
    contents = soup.select(
        "div.default_template_holder.page_container_inner div.wpb_column.vc_col-sm-4"
    )
    for row in contents:
        info = row.get_text(strip=True, separator="@@").split("@@Opening Hours:")
        if len(info) == 1:
            continue
        addr = info[0].split("@@")
        location_name = addr[0].strip()
        raw_address = " ".join(addr[1:-1]).strip().split(",")
        street_address = " ".join(raw_address[:-1]).replace("\xa0", "").strip()
        city = "Singapore"
        state = MISSING
        zip_postal = (
            raw_address[-1]
            .replace("Singapore", "")
            .replace("S", "")
            .replace("\xa0", "")
            .strip()
        )
        phone = addr[-1].replace("Tel:", "").strip()
        hours_of_operation = info[1].replace("@@", ",").lstrip(",").strip()
        location_type = MISSING
        country_code = "SG"
        store_number = MISSING
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
            raw_address=f"{street_address}, {city}, {zip_postal}",
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
