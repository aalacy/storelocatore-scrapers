from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "bamboo-gardens.com"
BASE_URL = "https://bamboo-gardens.com"
LOCATION_URL = "https://bamboo-gardens.com/inchins-bamboo-garden-locations/"
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
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    page_urls = soup.find("main").find_all("a", {"class": "wp-block-button__link"})
    for row in page_urls:
        parent_btn = row.parent.parent
        location_name = (
            parent_btn.find_previous_sibling("p")
            .find_previous_sibling("p")
            .find_previous_sibling("h1")
            .text.strip()
        )
        if "Virtual Kitchen" in location_name:
            continue
        try:
            page_url = row["href"]
            if "san-mateo-ca" in page_url:
                continue
            info = (
                pull_content(page_url)
                .find("main")
                .find("div", {"class": "fy-page-content fy-content js-images"})
            )
            location_name = info.find("h2").text.strip()
            if "Virtual Kitchen" in location_name:
                continue
            raw_address = (
                info.find("h2").find_next("p").get_text(strip=True, separator=",")
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = re.sub(
                r"Fax.*",
                "",
                info.find("ul").find_next("p").text.replace("Tel:", "").strip(),
            )
            hours_of_operation = (
                info.find("ul")
                .get_text(strip=True, separator=",")
                .replace("Banquet hall available for up to 350 guests", " ")
                .replace(",Event Space: Up to 120 guests", " ")
                .replace(",:", ",")
                .replace(":,", ":")
            )
        except:
            page_url = LOCATION_URL
            raw_address = (
                parent_btn.find_previous_sibling("p")
                .find_previous_sibling("p")
                .get_text(strip=True, separator=",")
            )
            street_address, city, state, zip_postal = getAddress(raw_address)
            phone = re.sub(
                r"Fax.*",
                "",
                parent_btn.find_previous_sibling("p").text.replace("Tel:", "").strip(),
            )
            hours_of_operation = (
                parent_btn.find_next("ul")
                .get_text(strip=True, separator=",")
                .replace("Banquet hall available for up to 350 guests", " ")
                .replace(",Event Space: Up to 120 guests", " ")
                .replace(",:", ":")
                .replace(":,", ":")
            )
        store_number = MISSING
        country_code = "US"
        location_type = "bamboo-gardens"
        latitude = MISSING
        longitude = MISSING
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
