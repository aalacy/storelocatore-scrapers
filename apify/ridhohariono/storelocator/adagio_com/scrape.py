from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re
from sgscrape.sgpostal import parse_address_intl

DOMAIN = "adagio.com"
BASE_URL = "https://www.adagio.com"
LOCATION_URL = "https://www.adagio.com/stores/"
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


def get_latlong(element):
    if not element:
        return MISSING, MISSING
    latlong = re.search(
        r"cbll=(\-?[0-9]+\.[0-9]+),(\-?[0-9]+\.[0-9]+)",
        element["src"],
    )
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_urls = soup.find("div", {"id": "stage"}).find_all("a")
    for row in store_urls:
        page_url = LOCATION_URL + row["href"]
        phone = row.parent.find("div").text
        soup = pull_content(page_url)
        content = soup.find("div", {"id": "stage"}).find(
            "div", {"class": "marginLeft marginRight"}
        )
        info = (
            content.find("div", {"style": "float:left;"})
            .get_text(strip=True, separator="@")
            .replace("|@GET DIRECTIONS", "")
            .replace("\n\t\t", ",")
            .strip()
        ).split("@")
        location_name = info[0]
        del info[0]
        raw_address = ", ".join(info)
        street_address, city, state, zip_postal = getAddress(raw_address)
        hours_of_operation = (
            content.find("div", {"style": "float:right;text-align:right;"})
            .get_text(strip=True, separator=",")
            .replace(":,", ": ")
            .strip()
        )
        store_number = MISSING
        country_code = "US"
        location_type = "adagio"
        map_link = soup.find("iframe", {"aria-label": "map of location"})
        latitude, longitude = get_latlong(map_link)
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
