from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "maxschicken.com"
LOCATION_URL = "https://www.maxschicken.com/page/store-locator"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)

MISSING = "<MISSING>"


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
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def get_hoo(url):
    soup = pull_content(url)
    hoo_content = soup.find("div", id=re.compile(r"dine-in-\d"))
    if not hoo_content:
        hoo_content = soup.find("div", id=re.compile(r"curbside-\d"))
    if not hoo_content:
        hoo_content = soup.find("div", id="-0")
    hours = (
        hoo_content.find("table")
        .get_text(strip=True, separator=",")
        .replace("day,", "day: ")
    ).strip()
    return hours


def fetch_data():
    log.info("Fetching store_locator data")
    states = session.get(
        "https://www.maxschicken.com/store_locator/get_area", headers=HEADERS
    ).json()
    exclude = ["United States", "Canada"]
    for state in states:
        if (
            state["area_description"] == "International"
            or state["area_name"] in exclude
        ):
            continue
        url_state = (
            "https://www.maxschicken.com/store_locator/get_cities_by/"
            + state["area_id"]
        )
        cities = session.get(url_state, headers=HEADERS).json()
        log.info(f"Found {len(cities)} cities in state {state['area_name']}")
        for city in cities:
            url_branch = (
                "https://www.maxschicken.com/store_locator/get_branch_by/"
                + city["city_id"]
            )
            branches = session.get(url_branch, headers=HEADERS).json()
            if not branches:
                log.info(f"Branch not found in city {city['city_name']}")
                continue
            log.info(f"Found {len(branches)} branches in city {city['city_name']}")
            for branch in branches:
                url_store = (
                    "https://www.maxschicken.com/store_locator/get_store_by/"
                    + branch["branch_id"]
                )
                stores = session.get(url_store, headers=HEADERS).json()
                if not stores:
                    log.info(f"Store not found in branch {branch['branch_name']}")
                    continue
                log.info(
                    f"Found {len(stores)} stores in branch {branch['branch_name']}"
                )
                for store in stores:
                    location_name = store["store_name"]
                    temp_city = city["city_name"].replace("City", "")
                    street_address = " ".join(
                        store["store_address"]
                        .replace(city["city_name"], "")
                        .replace(temp_city, "")
                        .replace("City", "")
                        .replace("\u00a0", " ")
                        .replace(", ,", " ")
                        .strip()
                        .split()
                    ).strip(",")
                    zip_postal = MISSING
                    phone = store["store_contact"].split("/")[0].strip()
                    country_code = "PH"
                    country_code = MISSING
                    store_number = store["store_id"]
                    hours_of_operation = (
                        bs(store["store_schedule"], "lxml")
                        .text.replace("Business Hours:", "")
                        .replace("Business Schedule:", "")
                        .replace("STORE HOURS:", "")
                        .replace("STORE HOURS", "")
                        .replace(
                            "<!--td {border: 1px solid #ccc;}br {mso-data-placement:same-cell;}-->",
                            "",
                        )
                        .replace("\u00a0", " ")
                        .replace("\r\n", " ")
                        .replace("\n", "")
                        .strip()
                    ).rstrip(",")
                    latitude = store["store_latitude"]
                    longitude = store["store_longtitude"]
                    location_type = branch["branch_name"]
                    log.info("Append {} => {}".format(location_name, street_address))
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=LOCATION_URL,
                        location_name=location_name,
                        street_address=street_address,
                        city=city["city_name"],
                        state=state["area_name"],
                        zip_postal=zip_postal,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
