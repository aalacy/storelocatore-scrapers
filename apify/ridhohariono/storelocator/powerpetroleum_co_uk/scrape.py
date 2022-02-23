from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "powerpetroleum.co.uk"
BASE_URL = "https://www.powerpetroleum.co.uk"
LOCATION_URL = "https://powerpetroleum.co.uk/fuel-filling-stations/"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("p.txt-red.larger a")
    for row in contents:
        page_url = row["href"]
        store = pull_content(page_url).find(
            "div", {"class": "col-md-10 col-md-offset-1 txt-white z99"}
        )
        info = row.get_text(strip=True, separator="@@").split("@@")
        location_name = info[0].strip()
        addr = re.split(r"–|-", info[1].strip())
        if len(addr) > 2:
            street_address = addr[0].replace("\n", "")
            city = addr[1].replace("\n", "")
            state = MISSING
            zip_postal = addr[2].replace("\n", "")
        else:
            street_address = MISSING
            city = addr[0].replace("\n", "")
            state = MISSING
            zip_postal = addr[1].replace("\n", "")
        country_code = "UK"
        phone = store.find_next().text.strip()
        store_number = MISSING
        try:
            hours_of_operation = (
                store.find("h4", text="Opening Hours")
                .find_next("p")
                .text.replace("\n", ": ")
                .replace("–", "-")
                .strip()
            )
        except:
            hours_of_operation = MISSING
        latitude = MISSING
        longitude = MISSING
        if "Service Station" in location_name:
            location_type = "Service Station"
        else:
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
