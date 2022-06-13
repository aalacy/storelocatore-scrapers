import time
import json

from sglogging import sglog
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium import SgChrome
from selenium.webdriver.common.by import By

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "fullers.co.uk"
website = "https://www.fullers.co.uk"
MISSING = SgRecord.MISSING

api_json = "https://www.fullers.co.uk/ajax/directory/pubs/allpubs"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object_variable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def get_address(raw_address):
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
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    with SgChrome() as driver:
        driver.get_and_wait_for_request(api_json)
        source = driver.find_element(by=By.XPATH, value=".//pre").text
        stores = json.loads(source)["Data"]
        log.info(f"Total stores = {len(stores)}")
        for store in stores:
            hours_of_operation = MISSING
            location_type = MISSING
            page_url = f"{website}/pubs/pub-finder"

            store_number = get_JSON_object_variable(store, "PubId")
            location_name = get_JSON_object_variable(store, "AboutHeading")

            if "Hotel" in str(location_name):
                if store_number.startswith("H"):
                    location_type = "Hotel"
                elif store_number.startswith("P"):
                    location_type = "Pub & Hotel"
                elif store_number.startswith("T"):
                    location_type = "Pub & Hotel"
            else:
                location_type = "Pub"

            country_code = "GB"
            phone = get_JSON_object_variable(store, "PhoneNumber")
            latitude = get_JSON_object_variable(store, "Latitude")
            longitude = get_JSON_object_variable(store, "Longitude")
            if latitude == "0.00":
                continue

            raw_address = get_JSON_object_variable(store, "Address")

            street_address, city, state, zip_postal = get_address(raw_address)
            zip_postal = get_JSON_object_variable(store, "Postcode")

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
                country_code=country_code,
                phone=phone,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
