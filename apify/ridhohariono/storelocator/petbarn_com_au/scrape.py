from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
import re


DOMAIN = "petbarn.com.au"
STATE_API = "https://www.petbarn.com.au/store-finder/ajax/searchbycountry?countrycode=%22AU%22&query="
API_STORES = "https://www.petbarn.com.au/store-finder/ajax/load?q="
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
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


def fetch_data():
    log.info("Fetching store_locator data")
    store_type = [
        {
            "name": "Petbarn",
            "code": "pb",
        },
        {
            "name": "Greencross Vet",
            "code": "gx",
        },
        {
            "name": "City Farmers",
            "code": "cf",
        },
    ]
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.AUSTRALIA],
        expected_search_radius_miles=20,
        max_search_results=5,
    )
    for zipcode in search:
        single_state = session.get(STATE_API + str(zipcode), headers=HEADERS).json()[
            "data"
        ][0][0]
        try:
            single_state["id"]
        except:
            continue
        for type in store_type:
            state_url = (
                API_STORES + str(single_state["id"]) + "&storetype=" + type["code"]
            )
            log.info("Get Store from state => " + state_url)
            stores = bs(
                session.get(state_url, headers=HEADERS).json()["list"],
                "lxml",
            ).select("ul#location-list-ul li")
            for store in stores:
                page_url = (
                    store.find("a", {"class": "view-store-details"})["onclick"]
                    .split("viewStore('")[1]
                    .split("',")[0]
                )
                content = pull_content(page_url)
                store.find("h3", {"class": "st-loc-title"}).find("em").decompose()
                store.find("h3", {"class": "st-loc-title"}).find("div").decompose()
                location_name = store.find("h3", {"class": "st-loc-title"}).text.strip()
                raw_address = (
                    store.find("div", {"class": "location-list-store-address"})
                    .get_text(strip=True, separator=",")
                    .replace(",Australia", "")
                )
                street_address, city, state, zip_postal = getAddress(raw_address)
                if city == MISSING:
                    city = store.find("span", {"class": "suburb"}).text.strip()
                if state == MISSING:
                    state = single_state["statecode"]
                if zip_postal == MISSING:
                    zip_postal = store.find("span", {"class": "postcode"}).text.strip()
                street_address = (
                    re.sub(
                        city + r"|" + state + "|" + zip_postal,
                        "",
                        street_address,
                        flags=re.IGNORECASE,
                    )
                    .strip()
                    .rstrip(",")
                )
                country_code = "AU"
                phone = store.find("span", {"class": "store-phone"}).text.strip()
                hours_of_operation = re.sub(
                    r"\s?,?Public.*|\(.*\)|,\d{2}\/\d{2}.*|,\d{1}nd.*",
                    "",
                    " ".join(
                        content.find("div", {"class": "store-hours-container"})
                        .get_text(strip=True, separator=",")
                        .split()
                    ).strip(),
                    flags=re.IGNORECASE,
                ).strip()
                location_type = type["name"]
                store_number = store["data-id"]
                latitude, longitude = (
                    store.find("a", id="get-direction-link")["href"]
                    .split("daddr=")[1]
                    .split(",")
                )
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
                )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumAndPageUrlId,
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
