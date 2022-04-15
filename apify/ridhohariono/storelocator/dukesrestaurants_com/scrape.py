from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "dukesrestaurants.com"
BASE_URL = "https://dukesrestaurants.com"
LOCATION_URL = "https://www.dukesrestaurants.com/"
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
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("a", text="Locations").find_next("ul").find_all("li")
    for row in contents:
        page_url = row.find("a")["href"] + "/reservations-directions"
        content = pull_content(page_url)
        location_name = row.find("a").text
        raw_address = (
            content.find("div", {"class": "address"})
            .get_text(strip=True, separator="@")
            .replace("@Get Directions", "")
            .split("@")
        )
        phone = raw_address[-1]
        raw_address = ", ".join(raw_address[1:][:-1])
        street_address, city, state, zip_postal = getAddress(raw_address)
        hoo_content = content.find("div", {"id": "parking"})
        if not hoo_content.find("h4"):
            hoo = (
                content.find("h3", text="Restaurant Hours")
                .find_next("p")
                .get_text(strip=True, separator=",")
            )
        else:
            hours_element = content.find("div", {"id": "hours"})
            if hours_element and hours_element.find("p"):
                hoo = (
                    hours_element.get_text(strip=True, separator=",")
                    .replace("Restaurant Hours", "")
                    .lstrip(",")
                    .strip()
                )
            else:
                hoo_content.find("h4").decompose()
                hoo_content.find("p").decompose()
                hoo_content.find_all("p")[-1].decompose()
                hoo = re.sub(
                    r"All guests.*",
                    "",
                    content.find("div", {"id": "parking"})
                    .get_text(strip=True, separator=",")
                    .replace("Parking,", "")
                    .replace("Restaurant Hours", "")
                    .lstrip(",")
                    .strip(),
                )
        if "dukeswaikiki.com" in page_url:
            hoo = "Mon-Sun: 7:00am - 11:00pm"
        hours_of_operation = re.sub(r"\(.*?\)", "", hoo).strip()
        country_code = "US"
        store_number = MISSING
        location_type = "dukesrestaurants"
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
