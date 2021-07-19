import time
import json
from typing import Iterable

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.pause_resume import CrawlStateSingleton
from webdriver_manager.chrome import ChromeDriverManager
from sgselenium import SgChrome
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

import ssl

try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification


website = "https://www.chanel.com"
MISSING = "<MISSING>"
jsonUrl = "https://services.chanel.com/en_US/storelocator/getStoreList"


log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetchHeaders():
    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )
    driver = SgChrome(
        is_headless=True,
        user_agent=user_agent,
        executable_path=ChromeDriverManager().install(),
    ).driver()

    session = SgRequests().requests_retry_session()
    driver.get(f"{website}/us/storelocator")
    session.post(jsonUrl)
    x = 0
    while True:
        x = x + 1
        log.debug(f"Trying to find headers = {x}")
        if x == 10:
            break
        for request in driver.requests:
            if "getStoreList" not in request.url:
                continue
            try:
                data = "geocodeResults=%5B%7B%22address_components%22%3A%5B%7B%22long_name%22%3A%22United+States%22%2C%22short_name%22%3A%22US%22%2C%22types%22%3A%5B%22country%22%2C%22political%22%5D%7D%5D%2C%22geometry%22%3A%7B%22location%22%3A%7B%22lat%22%3A62.383752%2C%22lng%22%3A-140.875303%7D%2C%22location_type%22%3A%22APPROXIMATE%22%7D%2C%22types%22%3A%5B%22postal_code%22%5D%7D%5D&iframe=true&radius=70.00"

                response = session.post(jsonUrl, headers=request.headers, data=data)
                response_text = response.text

                if len(response_text) > 0 and '"stores"' in response_text:
                    driver.quit()
                    log.debug("found headers")
                    return request.headers
                else:
                    continue

            except Exception as e:
                log.error(f"Error:{e}")
        driver.get(f"{website}/us/storelocator")

    raise Exception("Can't able to get headers")


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def getHOO(list):
    hoo = []
    for data in list:
        if data["day"] and data["opening"]:
            hoo.append(f"{data['day']} {data['opening']}")
    if len(hoo) > 0:
        return "; ".join(hoo)
    return MISSING


def getStoreDetails(store, countryCode):
    location_type = MISSING
    store_number = getJSONObjectVariable(store, "id")
    location_name = getJSONObjectVariable(store, "translations.0.name")
    page_url = f"https://services.chanel.com/en_US/storelocator/store/{location_name.replace(' ','+')}-{store_number}.html"
    street_address = getJSONObjectVariable(store, "translations.0.address1")
    address2 = getJSONObjectVariable(store, "translations.0.address2")
    if address2 != MISSING:
        street_address = street_address + " " + address2

    city = getJSONObjectVariable(store, "cityname")
    zip_postal = getJSONObjectVariable(store, "zipcode")
    state = getJSONObjectVariable(store, "statename")

    country_code = countryCode.upper()

    phone = getJSONObjectVariable(store, "phone")
    latitude = getJSONObjectVariable(store, "latitude")
    longitude = getJSONObjectVariable(store, "longitude")
    hours_of_operation = getHOO(getJSONObjectVariable(store, "openinghours", []))

    if state == MISSING:
        raw_address = f"{street_address}, {city} {zip_postal}"
    else:
        raw_address = f"{street_address}, {city}, {state} {zip_postal}"

    return SgRecord(
        locator_domain=website,
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


def fetchRequest(http, lat, lng, headers=None, failed=0):
    if failed == 5:
        raise Exception("Can't able to get headers")

    if headers is None:
        headers = fetchHeaders()
    try:
        data = f"geocodeResults=%5B%7B%22address_components%22%3A%5B%7B%22long_name%22%3A%22United+States%22%2C%22short_name%22%3A%22US%22%2C%22types%22%3A%5B%22country%22%2C%22political%22%5D%7D%5D%2C%22geometry%22%3A%7B%22location%22%3A%7B%22lat%22%3A{lat}%2C%22lng%22%3A{lng}%7D%2C%22location_type%22%3A%22APPROXIMATE%22%7D%2C%22types%22%3A%5B%22postal_code%22%5D%7D%5D&iframe=true&radius=70.00"
        response = http.post(jsonUrl, headers=headers, data=data)
        response_text = response.text
        if len(response_text) > 0 and '"stores"' in response_text:
            return headers, json.loads(response_text)["stores"]
        else:
            log.info("Failed trying to get header again")
            return headers, fetchRequest(http, lat, lng, None, failed + 1)
    except Exception as e:
        log.info(f"Failed trying to get header again {e}")
        return headers, fetchRequest(http, lat, lng, None, failed + 1)


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    count = 0
    stores = []
    store_numbers = []

    state = CrawlStateSingleton.get_instance()
    headers = None
    for lat, lng in search:
        count = count + 1
        countryCode = search.current_country()
        rec_count = state.get_misc_value(
            search.current_country(), default_factory=lambda: 0
        )
        state.set_misc_value(countryCode, rec_count + 1)

        headers, newStores = fetchRequest(http, lat, lng, headers)
        for store in newStores:
            store_number = getJSONObjectVariable(store, "id")
            if store_number in store_numbers:
                continue
            storeDetails = getStoreDetails(store, countryCode)
            store_numbers.append(store_number)
            stores.append(storeDetails)
            yield storeDetails
        log.debug(
            f"{count}. from {countryCode}: {lat, lng} stores= {len(newStores)}; total = {len(stores)}"
        )


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    search = DynamicGeoSearch(country_codes=SearchableCountries.ALL)

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    log.debug("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        log.debug(
            country_code,
            ": ",
            state.get_misc_value(country_code, default_factory=lambda: 0),
        )
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
