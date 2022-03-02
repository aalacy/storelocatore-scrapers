from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "ocean-prime.com"
BASE_URL = "https://www.ocean-prime.com"
LOCATION_URL = "https://www.ocean-prime.com/locations"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_usa(raw_address)
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
    HEADERS["Referer"] = url
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
    contents = soup.select("div.contentPane dt a")
    for row in contents:
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        location_name = row.text.strip()
        raw_address = (
            store.find("h2", text="LOCATION")
            .find_next("p")
            .get_text(strip=True, separator=",")
            .replace(",Map & Directions »", "")
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = store.find("h2", text="CONTACT").find_next("p").text.strip()
        country_code = "US"
        store_number = MISSING
        hoo_content = store.find("h2", text="HOURS")
        if hoo_content:
            hours_of_operation = (
                hoo_content.find_next("p")
                .get_text(strip=True, separator=",")
                .replace("day,", "day: ")
                .strip()
            )
        else:
            try:
                hours_of_operation = (
                    store.find("u", text=re.compile(r"View more information and.*"))
                    .parent.parent.find_previous("p")
                    .get_text(strip=True, separator=",")
                )
            except:
                hours_of_operation = MISSING
        try:
            map_link = (
                store.find("h3", text="Directions to a Location")
                .find_next("ul", {"class": "mobile-links"})
                .find(
                    "li",
                    text=re.compile(
                        city + r",\s*" + state + r".*|" + location_name + r".*",
                        re.IGNORECASE,
                    ),
                )
                .find("a")["href"]
            )
            latitude, longitude = get_latlong(map_link)
        except:
            latitude = MISSING
            longitude = MISSING
        location_type = MISSING
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
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
