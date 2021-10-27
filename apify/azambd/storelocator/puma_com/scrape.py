from lxml import html
import time
from typing import Iterable
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

website = "puma.com"
MISSING = SgRecord.MISSING
STORE_JSON_URL = "https://about.puma.com/api/PUMA/Feature/Locations/StoreLocator/StoreLocator?coordinates={}%2C{}8&loadMore=5"
headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
}

log = sglog.SgLogSetup().get_logger(logger_name=website)


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


def fetch_single_store(http, store, countryCode):
    country_code = countryCode
    store_number = store["StoreId"]
    location_name = store["StoreName"]
    phone = store["PhoneNumber"]
    latitude = store["Lat"]
    longitude = store["Lng"]
    page_url = f"https://about.puma.com{store['Url']}"
    location_type = "Outlet" if "Outlet" in location_name else "Store"
    log.debug(f"Scrapping {page_url}...")
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


def fetch_records(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    state = CrawlStateSingleton.get_instance()

    for lat, lng in search:
        countryCode = search.current_country()
        pageUrl = STORE_JSON_URL.format(lat, lng)
        response = http.get(pageUrl)
        decoded_data = response.text.encode().decode("utf-8-sig")
        data = json.loads(decoded_data)
        if "StoreLocatorItems" in data:
            stores = data["StoreLocatorItems"]
            log.debug(f"Total stores from {lat}, {lng} ={len(stores)}")
            for store in stores:
                try:
                    yield fetch_single_store(http, store, countryCode.upper())
                    rec_count = state.get_misc_value(
                        countryCode, default_factory=lambda: 0
                    )
                    state.set_misc_value(countryCode, rec_count + 1)
                except Exception as e:
                    log.error(f"Fat store from  {lat}, {lng} message={e}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    country_codes = SearchableCountries.ALL
    search = DynamicGeoSearch(
        country_codes=country_codes, expected_search_radius_miles=50
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    log.debug("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        try:
            count = state.get_misc_value(country_code, default_factory=lambda: 0)
            log.debug(f"{country_code}: {count}")
        except Exception as e:
            log.info(f"Country codes: {country_code}, message={e}")
            pass
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
