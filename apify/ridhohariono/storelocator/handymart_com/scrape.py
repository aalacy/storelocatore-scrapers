import re
import json
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl


DOMAIN = "handymart.com"
BASE_URL = "https://www.handymart.com"
LOCATION_URL = "http://www.handymart.com/locations_handymart/"
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


def handle_missing(field):
    if field is None or (isinstance(field, str) and len(field.strip()) == 0):
        return "<MISSING>"
    return field


def parse_json(soup, js_variable):
    pattern = re.compile(
        r"var\s+" + js_variable + r"\s+= \{.*?\}", re.MULTILINE | re.DOTALL
    )
    script = soup.find("script", text=pattern)
    if script:
        info = script.string.replace("/* <![CDATA[ */", "").replace("/* ]]> */", "")
    else:
        return False
    parse = re.search(r"var\s+" + js_variable + r"\s+= (\{.*?\});", info)
    parse = parse.group(1)
    data = json.loads(parse)
    return data


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_address = (
        soup.find("table", {"class": "table table-bordered table-striped"})
        .find("tbody")
        .find_all("tr")
    )
    store_info = parse_json(soup, "wpgmaps_localize_marker_data")
    locations = []
    for index in store_info:
        page_url = LOCATION_URL
        location_name = "Handy Mart"
        address = store_info[index]["address"].replace("City", "").split(",")
        raw_address = store_info[index]["address"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        country_code = "US"
        store_number = index
        get_phone = soup.find("td", string=re.compile(address[0][:5] + r".*"))
        if get_phone:
            phone = get_phone.find_next("td").text.strip()
        else:
            get_phone = soup.find("td", string=re.compile(address[0][:3] + r".*"))
            phone = get_phone.find_next("td").text.strip()
        hours_of_operation = "<MISSING>"
        location_type = get_phone.parent()[0].find("img")["alt"].strip()
        latitude = handle_missing(store_info[index]["lat"])
        longitude = handle_missing(store_info[index]["lng"])
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    last_element = store_address[-1].find_all("td")
    if last_element[2].text not in [val[3] for val in locations]:
        address = last_element[1].text.strip().split(",")
        log.info("Append {} => {}".format(location_name, address[0]))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
            location_name="Handy Mart",
            street_address=address[0],
            city=address[1],
            state=address[2],
            zip_postal=MISSING,
            country_code="US",
            store_number="22",
            phone=last_element[2].text.strip(),
            location_type=last_element[0].find("img")["alt"].strip(),
            latitude=MISSING,
            longitude=MISSING,
            hours_of_operation=MISSING,
            raw_address=", ".join(address),
        )
    return locations


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
