import time
import json
from typing import Iterable

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import parse_address_intl

DOMAIN = "libertyx.com"
website = "https://libertyx.com"
MISSING = SgRecord.MISSING
json_url = f"{website}/xhr/mobile/list_locations"


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

    value = str(value).strip()
    if value == "None" or len(value) == 0:
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
        log.info(f"Addressing missing, {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data(http: SgRequests, search: DynamicGeoSearch) -> Iterable[SgRecord]:
    states = CrawlStateSingleton.get_instance()
    count = 0

    for lat, lng in search:
        lat = round(lat, 3)
        lng = round(lng, 3)

        count = count + 1
        data = f"query=&lat={lat}&lng={lng}"
        headers = {
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://libertyx.com/a/buy-bitcoin/locations",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = http.post(json_url, headers=headers, data=data)
        data = json.loads(response.text)
        stores = []  # type: ignore
        if "locations" in str(data):
            try:
                if "locations" in data:
                    stores = data["locations"]  # type: ignore
            except Exception:
                pass

        total = len(stores)
        log.debug(f"{count}. From <{lat}:{lng}> stores = {total}")
        countryCode = search.current_country()
        rec_count = states.get_misc_value(countryCode, default_factory=lambda: 0)
        states.set_misc_value(countryCode, rec_count + total)

        for store in stores:
            store_number = get_JSON_object_variable(store, "locid")
            hashid = get_JSON_object_variable(store, "hashid")
            if hashid == MISSING or store_number == MISSING:
                continue

            page_url = website + "/a/buy-bitcoin/locations/" + hashid
            location_name = get_JSON_object_variable(store, "name")
            location_type = get_JSON_object_variable(store, "location_type")
            raw_address = get_JSON_object_variable(store, "navigation_address")
            street_address, city, state, zip_postal = get_address(raw_address)
            phone = get_JSON_object_variable(store, "phonenumber")
            latitude = get_JSON_object_variable(store, "lat")
            longitude = get_JSON_object_variable(store, "lng")
            hours_of_operation = (
                get_JSON_object_variable(store, "hours")
                .replace("\n", " ")
                .replace("\r", " ")
                .replace("\t", " ")
                .strip()
            )
            country_code = countryCode.upper()

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
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=20
    )
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        with SgRequests() as http:
            for rec in fetch_data(http, search):
                writer.write_row(rec)
    state = CrawlStateSingleton.get_instance()
    log.debug("Printing number of records by country-code:")
    for country_code in SearchableCountries.USA:
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
