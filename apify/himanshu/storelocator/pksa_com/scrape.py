from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper


DOMAIN = "pksa.com"
BASE_URL = "https://www.pksa.com"
LOCATION_URL = "https://www.pksa.com/locations"
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
            raw_address = raw_address.replace(", Website", "")
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


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    store_info = soup.find_all("div", {"role": "gridcell"})
    for row in store_info:
        info = (
            row.find("p", {"class": "font_2"})
            .get_text(strip=True, separator="@")
            .replace("\n\t\t", ",")
            .strip()
        ).split("@")
        if "Website" in info[-1]:
            del info[-1]
        if "Phone" in info[-1]:
            phone = info[-1].replace("Phone:", "")
            raw_address = " ".join(info[:-1])
        else:
            phone = MISSING
            raw_address = " ".join(info)
        if "Phone" in raw_address:
            raw_address = raw_address.split("Phone")[0]
        location_name = row.find("h4").text.replace("\n", " ")
        street_address, city, state, zip_postal = getAddress(raw_address)
        hours_of_operation = MISSING
        store_number = MISSING
        country_code = "US"
        location_type = "US LOCATION"
        if "India" in location_name:
            country_code = "INDIA"
            location_type = "INDIA LOCATION"
        latitude = MISSING
        longitude = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.PAGE_URL, SgRecord.Headers.STREET_ADDRESS})
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
