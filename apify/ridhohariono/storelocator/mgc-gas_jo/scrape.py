from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "mgc-gas.jo"
BASE_URL = "https://www.mgc-gas.jo"
LOCATION_URL = "https://www.mgc-gas.jo/gasStations/"
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


def get_latlong(url):
    latlong = re.search(r"@(-?[\d]*\.[\d]*),(-?[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select(
        "div.station-location-tabs-content div.station-location-info-card-name"
    )
    for row in contents:
        page_url = "https:" + row.find("a")["href"].replace("’", "%E2%80%99")
        info = pull_content(page_url)
        location_name = row.text.strip()
        raw_address = (
            info.find("div", {"class": "our-location-location-text"})
            .get_text(strip=True, separator=",")
            .replace("before main entrance of Arab Potash Co.", "")
        )
        street_address, city, _, _ = getAddress(raw_address)
        state = MISSING
        zip_postal = MISSING
        if "Madaba" in raw_address:
            city = "Madaba"
        if "Karak" in raw_address:
            city = "Karak"
        if "Mafraq" in raw_address:
            city = "Mafraq"
        city = city.replace("On Kings Highway", "").strip()
        phone = info.find("div", {"class": "our-location-phone-text"}).text.strip()
        country_code = "JO"
        store_number = MISSING
        hours_of_operation = MISSING
        latlong_content = info.find("script", string=re.compile(r"var\s+lat\s+=.*"))
        try:
            latitude = (
                re.search(r"lat\s+=(.*);", latlong_content.string).group(1).strip()
            )
            longitude = (
                re.search(r"lng\s+=(.*);", latlong_content.string).group(1).strip()
            )
        except:
            latitude = MISSING
            longitude = MISSING
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
