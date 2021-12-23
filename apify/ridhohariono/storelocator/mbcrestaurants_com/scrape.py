from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "mbcrestaurants.com"
BASE_URL = "https://www.mbcrestaurants.com"
LOCATION_URL = "https://www.mbcrestaurants.com/#"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2
            city = data.city
            state = data.state
            zip_postal = data.postcode

            if street_address is None or len(street_address) == 0:
                street_address = MISSING
            if city is None or len(city) == 0:
                city = MISSING
            if state is None or len(state) == 0:
                state = MISSING
            if zip_postal is None or len(zip_postal) == 0:
                zip_postal = MISSING
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No valid address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def pull_content(url):
    log.info("Pull content => " + url)
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_latlong(url):
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return "<MISSING>", "<MISSING>"
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    page_urls = soup.find_all(
        "a", {"class": "elementor-button-link elementor-button elementor-size-sm"}
    )
    for row in page_urls:
        page_url = row["href"]
        content = pull_content(page_url)
        info = content.find("div", {"data-id": "3070dfe"})
        location_name = content.find("title").text.split(" - ")[0].strip()
        raw_address = (
            info.find("div", {"data-id": re.compile(r"90d15e6|bc98c18")})
            .get_text(strip=True, separator="@")
            .split("@")
        )
        phone = raw_address[-1]
        if "BEER" in phone:
            phone = phone.replace("BEER", "2337").replace("(2337)", "")
        if "BREW" in phone:
            phone = phone.replace("BREW", "2739").replace("(2739)", "")
        del raw_address[-1]
        street_address, city, state, zip_postal = getAddress(", ".join(raw_address))
        if "WAIKIKI" in location_name:
            city = "Honolulu"
            state = "HI"
            zip_postal = "96815"
        hours_of_operation = info.find(
            "div", {"data-id": re.compile(r"21b3cf0|b2012c8")}
        ).get_text(strip=True, separator=",")
        if "3:30pm – 10:00pm Mon – Wed" in hours_of_operation:
            hoo = (
                hours_of_operation.replace("Mon – Wed", "")
                .replace("Thurs – Sun", "")
                .split(",")
            )
            hours_of_operation = "Mon - Wed " + hoo[0] + ",Thurs – Sun " + hoo[1]
        country_code = "US"
        store_number = MISSING
        location_type = "mbcrestaurants"
        map_link = content.find("div", {"data-id": "a712920"}).find("iframe")["src"]
        latitude, longitude = get_latlong(map_link)
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
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
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
