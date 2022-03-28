from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "genisyscu.org"
BASE_URL = "https://www.genisyscu.org"
LOCATION_URL = "https://www.genisyscu.org/locations"
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
    longlat = re.search(r"!2d(-[\d]*\.[\d]*)\!3d(-?[\d]*\.[\d]*)", url)
    if not longlat:
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("section.inside ul li a")
    for row in contents:
        if "grand-rapids-area" in row["href"]:
            continue
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        info = store.select_one("article div.row")
        location_name = row.text.strip()
        addr = info.find_all("p", {"class": "largesub"})
        try:
            raw_address = addr[0].get_text(strip=True, separator=",")
            phone = (
                addr[1]
                .get_text(strip=True, separator=",")
                .replace("Call or Text:", "")
                .split(",")[0]
                .split("x")[0]
                .replace("Call:", "")
                .strip()
            )
            hours_of_operation = (
                info.find("span", {"class": "day"})
                .parent.get_text(strip=True, separator=" ")
                .replace("*", "")
            )
        except:
            addr = row.parent.get_text(strip=True, separator="@@").split("@@")
            raw_address = ", ".join(addr[:-2]).strip()
            phone = addr[-2].strip()
            hours_of_operation = MISSING
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        latitude = MISSING
        longitude = MISSING
        store_number = MISSING
        location_type = "BRANCH"
        map_link = store.find("iframe", {"src": re.compile(r"maps\/embed.*")})["src"]
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
    with SgWriter(SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
