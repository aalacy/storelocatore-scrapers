from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import json

DOMAIN = "allstarglass.net"
BASE_URL = "https://www.allstarglass.net"
LOCATION_URL = "https://www.allstarglass.net/locations"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find("div", {"class": "paragraph__content"}).find_all("a")
    for row in contents:
        store_state = row.text.replace("Serving ", "").strip().lower()
        if "fivestarautoglass" in row["href"]:
            api_url = (
                "https://www.fivestarautoglass.net/api/feed/locations/" + store_state
            )
            base = "https://www.fivestarautoglass.net"
        else:
            api_url = BASE_URL + "/api/feed/locations/" + store_state
            base = BASE_URL
        log.info("Fetch data from api => " + api_url)
        data = session.post(api_url, headers=HEADERS).json()
        for store in data:
            page_url = base + store["url"]
            info = pull_content(page_url)
            location_name = store["title"]
            addr = json.loads(info.find("script", type="application/ld+json").string)[
                "@graph"
            ][0]
            try:
                street_address = addr["address"]["streetAddress"]
                city = addr["address"]["addressLocality"]
                state = addr["address"]["addressRegion"]
                zip_postal = addr["address"]["postalCode"]
                raw_address = f"{street_address}, {city}, {state}, {zip_postal}"
            except:
                addr_content = (
                    info.find("div", {"class": "article__store"})
                    .get_text(strip=True, separator="@@")
                    .split("@@")
                )
                raw_address = (
                    " ".join(", ".join(addr_content[:-1]).split())
                    .replace("Auto Glass Repair,", "")
                    .strip()
                )
                street_address, city, state, zip_postal = getAddress(raw_address)
            street_address = street_address.replace(state, "").replace(city, "").strip()
            prevent_missing = page_url.replace(base + "/locations/", "").split("/")
            if state is MISSING:
                state = prevent_missing[0].replace("-", " ").title()
            if city is MISSING:
                city = prevent_missing[2].replace("-", " ").title()
            if "geo" in addr:
                latitude = addr["geo"]["latitude"]
                longitude = addr["geo"]["longitude"]
            else:
                latitude = MISSING
                longitude = MISSING
            phone = info.find("div", {"class": "article__store-number"}).text.strip()
            country_code = "US"
            store_number = MISSING
            try:
                hoo = ""
                for hours in addr["openingHoursSpecification"]:
                    hoo += hours["dayOfWeek"] + ","
                hours_of_operation = hoo.rstrip(",")
            except:
                hours_of_operation = MISSING
            location_type = addr["@type"]
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
