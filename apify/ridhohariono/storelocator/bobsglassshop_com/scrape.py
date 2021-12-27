from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgpostal import parse_address_usa
import re

DOMAIN = "bobsglassshop.com"
BASE_URL = "https://www.bobsglassshop.com"
IFRAME = "https://admin699200.wixsite.com/bobsglassshop"
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(IFRAME).find("div", id="comp-jdwdh6p9")
    soup.find("p").decompose()
    soup.find("span", {"class": "wixGuard"}).parent.decompose()
    soup.find("p").decompose()
    contents = soup.find_all("p")
    for x in contents:
        if len(x.get_text(strip=True)) == 0:
            x.extract()
    get_addr = soup.get_text(strip=True, separator="@@").replace(
        "@@Bobs Glass Shop", ""
    )
    addresses = re.split(r"\(\d{2,3}\)\s+\d{3,4}-\d{3,4}", get_addr)
    addresses = list(filter(None, addresses))
    phone_numbers = re.findall(r"\(\d{2,3}\)\s+\d{3,4}-\d{3,4}", get_addr)
    for i in range(len(addresses)):
        info = re.sub(r"^@@|@@$", "", addresses[i]).split("@@")
        if len(info) > 3:
            info = info[1:]
        raw_address = ", ".join(info)
        street_address, city, state, zip_postal = getAddress(raw_address)
        if street_address == "Vanowen St":
            street_address = "11129 Vanowen St"
        street_address = street_address.replace(city, "").strip()
        if len(info) > 2:
            location_name = info[0]
        else:
            location_name = city
        phone = phone_numbers[i].strip()
        country_code = "US"
        store_number = MISSING
        hours_of_operation = MISSING
        latitude = MISSING
        longitude = MISSING
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=BASE_URL,
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
