import time
from typing import Iterable
import json

from sgrequests import SgRequests
from sglogging import SgLogSetup

from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "dodge.com"
MISSING = SgRecord.MISSING
STORE_JSON_URL = "https://www.dodge.com/bdlws/MDLSDealerLocator?brandCode=D&func=SALES&radius=50&resultsPage=1&resultsPerPage=100&zipCode={}"


log = SgLogSetup().get_logger("dodge_com")


def parse_hours(json_hours):
    days = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    hours = []
    for day in days:
        if json_hours[day]["closed"]:
            hours.append(f"{day}: closed")
        else:
            open_time = (
                json_hours[day]["open"]["time"] + " " + json_hours[day]["open"]["ampm"]
            )
            close_time = (
                json_hours[day]["close"]["time"]
                + " "
                + json_hours[day]["close"]["ampm"]
            )
            hours.append(f"{day}: {open_time}-{close_time}")
    return ", ".join(hours)


def handle_missing(x):
    if not x:
        return MISSING
    return x


def fetch_single_store(http, dealer, countryCode):
    country_code = countryCode
    store_number = handle_missing(dealer["dealerCode"])
    typ = "<MISSING>"
    name = handle_missing(dealer["dealerName"])
    add = handle_missing(dealer["dealerAddress1"])
    add2 = dealer["dealerAddress2"]
    if add2:
        add = f"add {add2}"
    state = handle_missing(dealer["dealerState"])
    city = handle_missing(dealer["dealerCity"])
    zc = handle_missing(dealer["dealerZipCode"][0:5])
    purl = handle_missing(dealer["website"])
    phone = handle_missing(dealer["phoneNumber"])
    lat = handle_missing(dealer["dealerShowroomLatitude"])
    lng = handle_missing(dealer["dealerShowroomLongitude"])
    hours = parse_hours(dealer["departments"]["sales"]["hours"])

    return SgRecord(
        locator_domain=website,
        page_url=purl,
        location_name=name,
        street_address=add,
        city=city,
        state=state,
        zip_postal=zc,
        country_code=country_code,
        phone=phone,
        location_type=typ,
        store_number=store_number,
        latitude=lat,
        longitude=lng,
        hours_of_operation=hours,
    )


def fetch_records(http: SgRequests, search: DynamicZipSearch) -> Iterable[SgRecord]:
    state = CrawlStateSingleton.get_instance()

    for code in search:
        countryCode = search.current_country()
        url = STORE_JSON_URL.format(code)
        response = http.get(url)
        decoded_data = response.text.encode().decode("utf-8-sig")
        data = json.loads(decoded_data)
        if "error" in data:
            continue
        dealers = data["dealer"]
        log.info(f"found {len(dealers)} dealers")

        for store in dealers:
            try:
                yield fetch_single_store(http, store, countryCode.upper())
                rec_count = state.get_misc_value(countryCode, default_factory=lambda: 0)
                state.set_misc_value(countryCode, rec_count + 1)
            except Exception as e:
                log.error(f"Fat store from  {code}, message={e}")


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )

    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        with SgRequests() as http:
            for rec in fetch_records(http, search):
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
