import time
import json
import re
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

from concurrent import futures

website = "https://www.timberland.de"
page_url = f"{website}/utility/handlersuche.html"
json_url = "https://hosted.where2getit.com/timberland/timberlandeu/rest/locatorsearch"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Content-Type": "application/json",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def json_object(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    if value is None:
        return MISSING
    value = str(value)
    if len(value) == 0:
        return MISSING
    return value


def get_sa(store):
    sa1 = json_object(store, "address1")
    sa2 = json_object(store, "address2")
    sa3 = json_object(store, "address3")
    if sa1 == MISSING and sa2 == MISSING and sa3 == MISSING:
        return MISSING
    address = []
    if sa1 != MISSING:
        address.append(sa1)
    if sa2 != MISSING:
        address.append(sa2)
    if sa3 != MISSING:
        address.append(sa3)
    return ", ".join(address)


def get_hoo(store):
    days = ["m", "t", "w", "thu", "f", "sa", "su"]
    WeekDays = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hoo = []
    count = -1
    for day in days:
        count = count + 1
        value = json_object(store, day)
        if value != MISSING:
            hoo.append(f"{WeekDays[count]}: {value}")

    if len(hoo) == 0:
        return MISSING
    return ", ".join(hoo)


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def get_data(coord, sgw: SgWriter):
    latitude, longitude = coord
    store_numbers = []
    try:
        payload = {
            "request": {
                "appkey": "2047B914-DD9C-3B95-87F3-7B461F779AEB",
                "formdata": {
                    "geoip": "start",
                    "dataview": "store_default",
                    "atleast": 1,
                    "limit": 1000,
                    "geolocs": {
                        "geoloc": [
                            {
                                "addressline": "",
                                "country": "",
                                "latitude": latitude,
                                "longitude": longitude,
                            }
                        ]
                    },
                    "searchradius": "1000",
                    "radiusuom": "km",
                    "order": "retail_store,outletstore,authorized_reseller,_distance",
                },
                "geoip": 1,
            }
        }
        response = session.post(json_url, headers=headers, data=json.dumps(payload))
        stores = json.loads(response.text)["response"]["collection"]

        log.info(f"from {latitude}: {longitude} ==> stores={len(stores)} ")

        for store in stores:
            store_number = json_object(store, "uid")
            location_name = (
                json_object(store, "name")
                .replace("<br>", " ")
                .replace("&reg", " ")
                .replace("; -", "- ")
                .replace(";", "")
            )
            location_name = (" ".join(location_name.split())).strip()
            street_address = get_sa(store)
            city = json_object(store, "city")
            zip_postal = json_object(store, "postalcode")
            state = json_object(store, "state")
            country_code = json_object(store, "country")
            phone = get_phone(json_object(store, "phone"))

            location_type_check = json_object(store, "retail_store")
            if location_type_check == "1":
                location_type = "Timberland Store"
            else:
                location_type = "Timberland Outlet"

            latitude = json_object(store, "latitude")
            longitude = json_object(store, "longitude")

            hours_of_operation = get_hoo(store)

            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )
            raw_address = " ".join(raw_address.split())
            raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
            if raw_address[len(raw_address) - 1] == ",":
                raw_address = raw_address[:-1]
            if store_number in store_numbers:
                continue
            store_numbers.append(store_number)

            row = SgRecord(
                locator_domain="timberland.de",
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
            sgw.write_row(row)

    except Exception as e:
        log.error(f"Can't load from {latitude}: {longitude} e={e}")


def fetch_data(sgw: SgWriter):
    postals = DynamicGeoSearch(
        country_codes=SearchableCountries.ALL,
        expected_search_radius_miles=621.371,
        max_search_results=1000,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in postals}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    CrawlStateSingleton.get_instance().save(override=True)

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        fetch_data(writer)

    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")
