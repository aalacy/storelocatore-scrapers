from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "grifolsplasma.com"
LOCATION_URL = "https://www.grifolsplasma.com/en/locations/find-a-donation-center"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
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
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.nearby-center-detail a")
    page_urls = list(dict.fromkeys(contents))
    for row in page_urls:
        if "Biomat" not in row.text:
            continue
        page_url = row["href"]
        info = pull_content(page_url)
        location_name = row.text.strip()
        phone = info.find("p", {"class": "telephone desktop"}).text
        info.find("p", {"class": "telephone desktop"}).decompose()
        info.find("p", {"class": "telephone mobile"}).decompose()
        addr = (
            info.find("div", {"class": "center-address"})
            .get_text(strip=True, separator="@@")
            .split("@@")
        )
        raw_address = ", ".join(addr[1:]).strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        zip_postal = zip_postal.replace("999-999-9999", "")
        hoo_content = info.select(
            "div.bottom-information div.center-column-2  p.hours:nth-child(-n+10)"
        )
        hours_of_operation = ""
        for hoo in hoo_content:
            day = hoo.find("span", {"class": "day-name"}).text.strip()
            hour = hoo.find("span", {"class": "day-time"}).text.strip()
            hours_of_operation += day + " " + hour + ","
        hours_of_operation = hours_of_operation.rstrip(",")
        latitude = MISSING
        longitude = MISSING
        country_code = "US"
        store_number = MISSING
        check_status = info.find("div", {"class": "center-information"}).text.strip()
        if "Coming soon" in check_status:
            location_type = "COMING_SOON"
        elif "Temporarily closed" in check_status:
            location_type = "TEMPORARILY_CLOSED"
        else:
            location_type = "BIOMAT"
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
