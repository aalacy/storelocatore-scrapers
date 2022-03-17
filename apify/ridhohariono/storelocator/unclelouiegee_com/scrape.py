from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re


DOMAIN = "unclelouiegee.com"
LOCATION_URL = "http://unclelouiegee.com/locations/page/{}?wpbdp_view=all_listings"
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
            data = parse_address_usa(raw_address)
            street_address = data.street_address_1
            if data.street_address_2 is not None:
                street_address = f"{street_address} {data.street_address_2}"
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


def fetch_data():
    log.info("Fetching store_locator data")
    page = 1
    while True:
        soup = pull_content(LOCATION_URL.format(page))
        stores = soup.select("div#wpbdp-listings-list div.wpbdp-listing")
        if not stores:
            break
        for row in stores:
            page_url = row.find("div", {"class": "listing-title"}).find("a")["href"]
            location_name = row.find("div", {"class": "listing-title"}).text.strip()
            coming_soon = re.search(r"Coming Soon", location_name, flags=re.IGNORECASE)
            if not coming_soon:
                info = row.find("div", {"class": "listing-details"})
                raw_address = re.sub(
                    r"\(.*\)",
                    "",
                    info.find("span", text="Business Location")
                    .find_next("div", {"class": "value"})
                    .get_text(strip=True, separator=" ")
                    .replace("-", " ")
                    .replace(":", ",")
                    .replace("/", ",")
                    .strip(),
                )
                street_address, city, state, zip_postal = getAddress(raw_address)
                if "Tampa" in raw_address:
                    city = "Tampa"
                if "Queens" in raw_address:
                    city = "Queens"
                street_address = re.sub(
                    r".*Island|^\D+:|" + city + r"|" + state, "", street_address
                ).strip()
                country_code = "US"
                try:
                    phone = re.sub(
                        r"\(\D+\)",
                        "",
                        info.find("span", text="Business Phone Number")
                        .find_next("div", {"class": "value"})
                        .text.strip(),
                    ).split("/")[0]
                except:
                    phone = MISSING
                hours_of_operation = MISSING
                store_number = MISSING
                location_type = MISSING
                pattern = location_name.split(":")[-1].split(".")[0].split(",")[0]
                try:
                    latlong = soup.find(
                        "div", {"class": "TO-EDIT-MAP-USE-PAGE-BUILDER"}
                    ).find("div", {"data-title": re.compile(pattern + r".*")})
                    latitude = latlong["data-lat"]
                    longitude = latlong["data-lng"]
                except:
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
        page += 1


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
