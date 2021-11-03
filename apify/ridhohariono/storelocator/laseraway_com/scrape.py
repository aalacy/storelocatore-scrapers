import re
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import json

DOMAIN = "laseraway.com"
BASE_URL = "https://www.laseraway.com/"
SITEMAP_URL = "https://www.laseraway.com/sitemap/"
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
    soup = bs(req.content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(SITEMAP_URL)
    content = soup.find("h4", text="Locations").parent.find_all("li")
    page_urls = list(set([row.find("a")["href"] for row in content]))
    for page_url in page_urls:
        check_url = page_url.replace("https://www.laseraway.com/locations/", "").split(
            "/"
        )
        if len(check_url) < 3:
            continue
        store = pull_content(page_url)
        location_name = (
            store.find("div", {"class": "location-map-hours"}).find("h4").text.strip()
        )
        info = store.find("script", {"id": "wpsl-js-js-extra"})
        info = re.search(r"var\s+wpslMap_0=(.*);", info.string).group(1)
        info = json.loads(info)
        street_address = (
            info["locations"][0]["address"] + " " + info["locations"][0]["address2"]
        ).strip()
        city = info["locations"][0]["city"]
        state = info["locations"][0]["state"]
        zip_postal = info["locations"][0]["zip"]
        country_code = info["locations"][0]["country"]
        store_number = MISSING
        phone = (
            store.find("div", {"class": "location-map-hours"})
            .find("address")
            .find("a", {"href": re.compile(r"tel.*")})
            .text.strip()
        )
        location_type = MISSING
        latitude = info["locations"][0]["lat"]
        longitude = info["locations"][0]["lng"]
        hours_of_operation = (
            store.find("div", {"class": "location-map-hours"})
            .find("table")
            .get_text(strip=True, separator=",")
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
            raw_address=f"{street_address}, {city}, {state}, {zip_postal}",
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.ZIP,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
