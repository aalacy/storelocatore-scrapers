import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_usa

DOMAIN = "ohnuts.com"
BASE_URL = "https://www.ohnuts.com"
LOCATION_URL = "https://www.ohnuts.com/retail.cfm"
HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_latlong(soup):
    element = soup.find(
        "script", string=re.compile(r"google\.maps\.event\.addDomListener")
    )
    latlong = re.search(
        r"google\.maps\.LatLng\((-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)\)", element.string
    )
    if not latlong:
        return MISSING
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    page_urls = soup.find("div", {"id": "stores-list"}).find_all(
        "a", {"class": "title"}
    )
    for row in page_urls:
        page_url = BASE_URL + row["href"]
        store = pull_content(page_url)
        location_name = row.text.strip()
        raw_address = store.find("span", {"class": "address"}).get_text(
            strip=True, separator=","
        )
        street_address, city, state, zip_postal = getAddress(raw_address)
        store_number = MISSING
        phone = re.search(
            r"Phone: (\d{3}-\d{3}-\d{3,4}),",
            store.find("div", {"class": "storeInfo"}).get_text(
                strip=True, separator=","
            ),
        ).group(1)
        country_code = "US"
        location_type = MISSING
        latitude, longitude = get_latlong(store)
        hoo_content = store.find("strong", text="General Store Hours:")
        try:
            hoo = (
                hoo_content.parent.parent.parent.get_text(strip=True, separator=",")
                .replace("Store Hours", "")
                .split("General :")
            )[1]
        except:
            hoo = store.find("div", {"class": "step"})
            hoo.find("div").decompose()
            hoo = hoo.get_text(strip=True, separator=",")
        hours_of_operation = (
            hoo.replace("day,", "day ")
            .replace("Two and half hour before sunset", " 6:00pm")
            .replace(",* Curb Side Pick Up is Available in this Location *", "")
            .replace(" ", "")
            .strip()
        ).lstrip(",")
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
