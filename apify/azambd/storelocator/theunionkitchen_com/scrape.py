import ssl
import time
import json
from lxml import html
from sgpostal.sgpostal import parse_address_usa
from sgselenium.sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sglogging import sglog

ssl._create_default_https_context = ssl._create_unverified_context

MISSING = SgRecord.MISSING
DOMAIN = "theunionkitchen.com"
website = "https://www.theunionkitchen.com"
location_type = "Restaurant"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
start_url = "https://www.theunionkitchen.com/locations"
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def get_address(raw_address):
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
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(start_url)
        driver.implicitly_wait(30)
        htmlpage = driver.page_source
        body = html.fromstring(htmlpage, "lxml")

        jsons = body.xpath('//script[contains(@id, "popmenu-apollo-state")]/text()')
        jsontext = (
            jsons[0]
            .split("window.POPMENU_APOLLO_STATE = ")[1]
            .replace(";\n", "")
            .strip()
        )
        data = json.loads(jsontext)
        res_id_nodes = data["CustomPageSection:82228"]["locations"]
        for rl in res_id_nodes:
            rl_id = rl["__ref"]
            slug = data[f"{rl_id}"]["slug"]
            page_url = f"{website}/{slug}"
            store_number = data[f"{rl_id}"]["id"]
            location_name = data[f"{rl_id}"]["name"]
            phone = data[f"{rl_id}"]["phone"]
            latitude = data[f"{rl_id}"]["lat"]
            longitude = data[f"{rl_id}"]["lng"]
            raw_address = data[f"{rl_id}"]["fullAddress"].replace("\n", " ")
            street_address, city, state, zip_postal = get_address(raw_address)
            hours_of_operation = ", ".join(data[f"{rl_id}"]["schemaHours"])

            yield SgRecord(
                locator_domain=DOMAIN,
                store_number=store_number,
                page_url=page_url,
                location_name=location_name,
                location_type=location_type,
                street_address=street_address,
                city=city,
                zip_postal=zip_postal,
                state=state,
                country_code="US",
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
