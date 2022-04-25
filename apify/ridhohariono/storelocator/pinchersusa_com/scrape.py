from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_intl
import re

DOMAIN = "pinchersusa.com"
BASE_URL = "https://www.pinchersusa.com"
LOCATION_URL = "https://www.pinchersusa.com/locations/"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    req = session.get(url, headers=HEADERS)
    if req.status_code == 404:
        return 404
    soup = bs(req.content, "lxml")
    return soup


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


def get_latlong(url):
    latlong = re.search(r"(-?[\d]*\.[\d]*),(-[\d]*\.[\d]*)", url)
    if not latlong:
        return "<MISSING>", "<MISSING>"
    return latlong.group(1), latlong.group(2)


def get_hoo(elements):
    hoo_content = elements.find_all("h2")
    del hoo_content[:4]
    if len(hoo_content) == 0:
        return MISSING
    hoo = " "
    for row in hoo_content:
        hoo += row.text + " "
    return hoo.strip()


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_locator = soup.find("section", {"id": "main_content"}).find_all(
        "div", {"class": "vc_column-inner vc_custom_1545241388299"}
    )
    for row in store_locator:
        info = row.find("div", {"class": "emboryo_module_custom_text"})
        location_name = (
            row.find("a", text="Menu")["href"]
            .replace("https://www.pinchersusa.com/", "")
            .replace("-menu", "")
            .replace("/", "")
            .replace("-", " ")
        ).title()
        raw_address = info.find("h2").text
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = MISSING
        phone = (
            info.find_all("h3")[1]
            .find_next("h2")
            .find_next("h2")
            .text.replace("Phone:\xa0", "")
        )
        hours_of_operation = get_hoo(info)
        map_url = row.find(
            "a", {"href": re.compile(r"https:\/\/www.google.com\/maps.*")}
        )
        latitude, longitude = get_latlong(map_url["href"])
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.RAW_ADDRESS,
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
