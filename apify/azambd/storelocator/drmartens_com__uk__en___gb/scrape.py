import re
from sgpostal.sgpostal import parse_address_intl
import time
import json
from typing import Iterable, Tuple, Callable

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import SearchableCountries
from sgzip.parallel import DynamicSearchMaker, ParallelDynamicSearch, SearchIteration

DOMAIN = "drmartens.com"
MISSING = SgRecord.MISSING
website = "https://www.drmartens.com"
store_url = f"{website}/uk/en_gb/store-finder"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

hdr = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36",
}


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


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


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
        log.info(f"Address Missing: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


class SearchIteration(SearchIteration):
    def __init__(self, http: SgRequests):
        self.__http = http
        self.__state = CrawlStateSingleton.get_instance()

    def do(
        self,
        coord: Tuple[float, float],
        zipcode: str,
        current_country: str,
        items_remaining: int,
        found_location_at: Callable[[float, float], None],
    ) -> Iterable[SgRecord]:
        stores = []
        page = 0

        zipcode = str(zipcode).replace(" ", "%20")
        while True:
            url = f"{store_url}?q={zipcode}&page={page}"
            response = self.__http.get(url, headers=hdr)
            try:
                newStores = (json.loads(response.text))["data"]
            except Exception as e:
                log.info(f"***Response has err: {e}")
                newStores = []
            stores = stores + newStores
            if len(newStores) < 10:
                break
            else:
                page = page + 1

        log.info(f"From {current_country}=> {zipcode} stores = {len(stores)}")

        rec_count = self.__state.get_misc_value(
            current_country, default_factory=lambda: 0
        )
        self.__state.set_misc_value(current_country, rec_count + len(stores))

        country_code = current_country.upper()

        for store in stores:
            store_number = MISSING
            location_type = MISSING
            page_url = store_url
            location_name = get_JSON_object_variable(store, "displayName")
            latitude = get_JSON_object_variable(store, "latitude")
            longitude = get_JSON_object_variable(store, "longitude")
            phone = get_phone(get_JSON_object_variable(store, "phone"))

            street_address = get_JSON_object_variable(store, "line1")
            line2 = get_JSON_object_variable(store, "line2")
            if line2 is not None and line2 != MISSING:
                street_address += " " + line2

            street_address = street_address.strip()
            town = get_JSON_object_variable(store, "town")
            postalCode = get_JSON_object_variable(store, "postalCode")
            hoo, city, state, zip_postal = get_address(
                f"{street_address} {town} {postalCode}"
            )

            if zip_postal == MISSING:
                zip_postal = postalCode

            raw_address = f"{street_address.strip()} {town} {postalCode}"

            hours_of_operation = []
            hoo = get_JSON_object_variable(store, "openings")
            if hoo is not None and hoo != MISSING:
                for day, hours in hoo.items():
                    hours_of_operation.append(f"{day} {hours}")

            hours_of_operation = " ".join(hours_of_operation)
            if len(hours_of_operation) == 0:
                hours_of_operation = MISSING

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
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    search_maker = DynamicSearchMaker(
        search_type="DynamicZipSearch", max_search_distance_miles=50
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        with SgRequests() as http:
            search_iter = SearchIteration(http=http)
            par_search = ParallelDynamicSearch(
                search_maker=search_maker,
                search_iteration=search_iter,
                country_codes=SearchableCountries.ALL,
                max_threads=1,
            )

            for rec in par_search.run():
                writer.write_row(rec)

    state = CrawlStateSingleton.get_instance()
    log.debug("Printing number of records by country-code:")
    for country_code in SearchableCountries.ALL:
        log.debug(
            f"{country_code}: {state.get_misc_value(country_code, default_factory=lambda: 0)}"
        )

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
