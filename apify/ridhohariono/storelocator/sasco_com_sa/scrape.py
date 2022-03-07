from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re
import ast

DOMAIN = "sasco.com.sa"
BASE_URL = "https://www.sasco.com.sa"
LOCATION_URL = "https://www.sasco.com.sa/english/stations-locator"
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
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return False
    soup = bs(req.content, "lxml")
    return soup


def get_latlong(soup):
    latlong_content = soup.find("script", string=re.compile(r"var\s+lat.*"))
    latlong = re.search(
        r"var\s+lat\s=\s+(\[.*\]);var\s+lng\s=\s+(\[.*\]);var\s+branch",
        latlong_content.string,
    )
    lat = ast.literal_eval(latlong.group(1))
    lng = ast.literal_eval(latlong.group(2))
    return lat, lng


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.find_all("a", {"class": "moreLink branchDetails"})
    lat, lng = get_latlong(soup)
    i = 0
    for row in contents:
        page_url = BASE_URL + row["href"]
        location_name = row.parent.parent.find(
            "div", {"class": "listingTitle"}
        ).text.strip()
        addr = (
            row.parent.get_text(strip=True, separator="@@")
            .replace("@@more", "")
            .split("@@")
        )
        raw_address = addr[0].strip()
        street_address, city, state, zip_postal = getAddress(raw_address)
        try:
            info = pull_content(page_url)
            phone = info.find("a", {"href": re.compile(r"tel:.*")}).text.strip()
        except:
            phone = MISSING
        location_type = MISSING
        country_code = "SA"
        store_number = MISSING
        if len(addr) > 1 and "pm" in addr[-1]:
            hours_of_operation = addr[-1]
        else:
            hours_of_operation = MISSING
        latitude = lat[i]
        longitude = lng[i]
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
        i += 1


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
