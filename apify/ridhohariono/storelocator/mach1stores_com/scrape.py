from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "mach1stores.com"
BASE_URL = "https://mach1stores.com"
LOCATION_URL = "https://mach1stores.com/locations"
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
        return MISSING, MISSING
    return longlat.group(2), longlat.group(1)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.all-results h5 a")
    for row in contents:
        page_url = BASE_URL + row["href"]
        if "mach-21-liquor-store" in page_url:
            continue
        store = pull_content(page_url).select_one("div.location-text div.container")
        info = store.find("div", {"class": "results-main"})
        location_name = info.find("h3").text.strip()
        addr = (
            info.find("div", {"class": "results"})
            .get_text(strip=True, separator="@@")
            .split("@@")
        )
        if len(addr) < 4:
            raw_address = ",".join(addr[:-1]).strip()
            phone = addr[-1]
            hours_of_operation = MISSING
        elif len(addr) > 4:
            raw_address = ",".join(addr[:-3]).strip()
            phone = addr[-3]
            hours_of_operation = ", ".join(addr[3:]).replace(" ", "").strip()
        else:
            raw_address = ",".join(addr[:-2]).strip()
            phone = addr[-2]
            hours_of_operation = addr[-1].replace(" ", "").strip()
        raw_address = raw_address.replace(" ", "").strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        phone = phone.replace("Phone: ", "").strip()
        country_code = "US"
        store_number = page_url.split("store-")[1]
        location_type = MISSING
        try:
            map_link = store.find("iframe")["src"]
            latitude, longitude = get_latlong(map_link)
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumAndPageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
