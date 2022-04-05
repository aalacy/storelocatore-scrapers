import time
import json
from concurrent.futures import ThreadPoolExecutor
from lxml import html
from typing import Iterable
import re
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

import pycountry

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

website = "puma.com"
MISSING = SgRecord.MISSING
STORE_JSON_URL = "https://about.puma.com/api/PUMA/Feature/Locations/StoreLocator/StoreLocator?coordinates={}%2C{}8&loadMore=50"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)
max_workers = 24

http = SgRequests()


def fetch_concurrent_list(stores, occurrence=max_workers):
    output = []
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetch_single_store, stores):
            if result is not None:
                output.append(result)
    return output


def do_fuzzy_search(country):
    try:
        result = pycountry.countries.search_fuzzy(country)
    except Exception:
        return MISSING
    else:
        return result[0].alpha_2


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_objectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


# get Phone, pull first phone number
def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetch_single_store(store, retry=0):
    try:
        countryjson = store["Country"]
        if "ROMANIA_EEMEA" in str(countryjson):
            countryjson = "ROMANIA"
        if "Lithuanta" in str(countryjson):
            countryjson = "Lithuania"

        country_code = do_fuzzy_search(countryjson)
        store_number = store["StoreId"]
        location_name = store["StoreName"]
        phone = get_phone(store["PhoneNumber"])
        latitude = store["Lat"]
        longitude = store["Lng"]
        page_url = f"https://about.puma.com{store['Url']}"
        location_type = "Outlet" if "Outlet" in location_name else "Store"

        log.info(f"Scrapping {page_url}...")
        response = http.get(page_url)
        body = html.fromstring(response.text, "lxml")

        data = body.xpath('//script[contains(@id, "current-store-details")]/text()')
        if len(data) == 0:
            storeData = {}
        else:
            storeData = json.loads(data[0])

        street_address = get_json_objectVariable(storeData, "address.streetAddress")
        city = get_json_objectVariable(storeData, "address.addressLocality")
        zip_postal = get_json_objectVariable(storeData, "address.postalCode")
        if str(zip_postal) == "0" or str(zip_postal) == "NA":
            zip_postal = MISSING

        state = get_json_objectVariable(storeData, "address.addressRegion")
        hours = get_json_objectVariable(storeData, "openingHoursSpecification", [])
        hoo = []
        for hour in hours:
            hoo.append(
                f"{hour['dayOfWeek']}: {hour['opens']} - {hour['closes']}".replace(
                    "http://schema.org/", ""
                )
            )

        hoo = "; ".join(hoo)
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
            hours_of_operation=hoo,
        )
    except Exception as e:
        if retry > 3:
            try:
                page_url = f"https://about.puma.com{store['Url']}"
                log.error(f"Error loading {page_url}, message={e}")
            except Exception as e1:
                log.error(f"Error , message={e1}")
                pass
            return None
        else:
            return fetch_single_store(store, retry + 1)


def fetch_records(search: DynamicGeoSearch) -> Iterable[SgRecord]:
    state = CrawlStateSingleton.get_instance()
    storeIds = [MISSING]
    totalStores = 0
    count = 0
    for lat, lng in search:
        count = count + 1
        countryCode = search.current_country()
        pageUrl = STORE_JSON_URL.format(lat, lng)
        response = http.get(pageUrl)
        decoded_data = response.text.encode().decode("utf-8-sig")
        data = json.loads(decoded_data)
        stores = []

        if "StoreLocatorItems" in data:
            for store in data["StoreLocatorItems"]:
                if store["StoreId"] in storeIds:
                    continue
                storeIds.append(store["StoreId"])
                stores.append(store)

        if len(stores) == 0:
            continue
        for store in fetch_concurrent_list(stores):
            try:
                yield store
                totalStores = totalStores + 1
                rec_count = state.get_misc_value(countryCode, default_factory=lambda: 0)
                state.set_misc_value(countryCode, rec_count + 1)
            except Exception as e:
                log.info(f"Error store from  <{lat}, {lng}> message={e}")

        log.info(
            f"{count}. Total stores from <{lat}, {lng}> = {len(stores)}; total = {totalStores}"
        )


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    country_codes = SearchableCountries.ALL
    search = DynamicGeoSearch(country_codes=country_codes, max_search_results=50)

    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_records(search):
            writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    log.info("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        try:
            count = state.get_misc_value(country_code, default_factory=lambda: 0)
            log.info(f"{country_code}: {count}")
        except Exception as e:
            log.info(f"Country codes: {country_code}, message={e}")
            pass
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
