import time
import json

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

DOMAIN = "fullers.co.uk"
website = "https://www.fullers.co.uk"
MISSING = SgRecord.MISSING
api_json = f"{website}/api/sitecore/findpubs?id=%7B07DC99EB-8AA2-42F4-B9A6-9D3648ABD465%7D&mode=LocationPub&filters=-1%2CStanding%2C&myPosition=(51.507351%2C+-0.127758)&position=(51.507351%2C+-0.127758)&nePosition=(52.68834732924637%2C+2.68748858203125)&swPosition=(50.29492984990391%2C+-2.94300458203125)&defaultRadius=&zoomLevel=8&findNearMe=false&pageHeading="
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


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


def fetch_data():
    with SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ) as driver:
        driver.get(api_json)
        source = driver.find_element_by_xpath(".//pre").text
        stores = json.loads(source)["pubs"]
        log.info(f"Total stores = {len(stores)}")
        for store in stores:
            hours_of_operation = MISSING
            location_type = MISSING
            page_url = f"{website}/pubs/old-pub-finder"

            store_number = get_JSON_object_variable(store, "PubId")
            location_name = get_JSON_object_variable(store, "PubSignageName")

            if "Hotel" in str(location_name):
                if store_number.startswith("H"):
                    location_type = "Hotel"
                elif store_number.startswith("P"):
                    location_type = "Pub & Hotel"
                elif store_number.startswith("T"):
                    location_type = "Pub & Hotel"
            else:
                location_type = "Pub"

            street_address = (
                get_JSON_object_variable(store, "PubAddressLine1")
                + " "
                + get_JSON_object_variable(store, "PubAddressLine2")
            ).strip()
            city = get_JSON_object_variable(store, "PubAddressCity")
            zip_postal = get_JSON_object_variable(store, "PubAddressPostcode")
            state = get_JSON_object_variable(store, "PubAddressCounty")
            country_code = "GB"
            phone = get_JSON_object_variable(store, "PubContactTelephone")
            latitude = get_JSON_object_variable(store, "Latitude")
            longitude = get_JSON_object_variable(store, "Longitude")
            if latitude == "0.00":
                continue
            raw_address = street_address

            if city != MISSING:
                raw_address = raw_address + ", " + city

            if state != MISSING:
                raw_address = raw_address + ", " + state

            raw_address = raw_address + " " + zip_postal
            raw_address = " ".join(raw_address.split())

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
