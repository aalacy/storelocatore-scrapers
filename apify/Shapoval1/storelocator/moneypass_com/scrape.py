import time
import json
from concurrent import futures

from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton

website = "https://moneypass.com/"
store_url = "https://locationapi.wave2.io/api/client/getlocations"
MISSING = SgRecord.MISSING
max_workers = 1

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Accept": "*/*",
    "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
    "Content-Type": "application/json; charset=UTF-8",
    "Origin": "https://moneypasswidget.wave2.io",
    "Connection": "keep-alive",
    "Referer": "https://moneypasswidget.wave2.io/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(zip_code):
    data = {
        "Latitude": "",
        "Longitude": "",
        "Address": zip_code,
        "City": "",
        "State": "",
        "Zipcode": "",
        "Country": "",
        "Action": "textsearch",
        "ActionOverwrite": "",
        "Filters": "FCS,FIITM,FIATM,ATMSF,ATMDP,ESC,",
    }
    try:
        response = session.post(store_url, headers=headers, data=json.dumps(data))
        stores = json.loads(response.text)["Features"]
        log.debug(f"From {zip_code} stores = {len(stores)}")
        return stores
    except Exception as e:
        log.error(f"can't able to get data from {zip_code}: {e}")
        return []


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_json_object(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
        if value is None:
            return noVal
    return value


def get_hoo(store):
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hoo = []

    for day in days:
        opens = get_json_object(store, f"{day}Open")
        closes = get_json_object(store, f"{day}Close")
        if len(opens) == 0:
            opens = MISSING
        if len(closes) == 0:
            closes = MISSING
        if opens == MISSING and closes == MISSING:
            continue
        if closes == MISSING:
            hoo.append(f"{day}: {opens}")
        elif opens == MISSING:
            hoo.append(f"{day}: {closes}")
        else:
            hoo.append(f"{day}: {opens} - {closes}")

    hoo = "; ".join(hoo)
    return hoo


def fetch_data():
    zip_codes = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], max_search_distance_miles=1
    )

    with futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        executors = {
            executor.submit(request_with_retries, zip_code): zip_code
            for zip_code in zip_codes
        }

        for future in futures.as_completed(executors):
            stores = future.result()
            for store in stores:
                properties = get_json_object(store, "Properties")

                location_name = get_json_object(properties, "LocationName")
                store_number = get_json_object(properties, "LocationId")
                page_url = "https://moneypass.com/atm-locator.html"
                street_address = get_json_object(properties, "Address")
                location_type = get_json_object(store, "LocationFeatures.LocationType")
                city = get_json_object(properties, "City")
                zip_postal = get_json_object(properties, "Postalcode")
                state = get_json_object(properties, "State")
                country_code = get_json_object(properties, "Country", "US")
                phone = get_json_object(properties, "Phone")
                latitude = get_json_object(properties, "Latitude")
                longitude = get_json_object(properties, "Longitude")
                hours_of_operation = get_hoo(properties)
                raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                    MISSING, ""
                )
                raw_address = " ".join(raw_address.split())
                raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
                if raw_address[len(raw_address) - 1] == ",":
                    raw_address = raw_address[:-1]

                yield SgRecord(
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
    return []


def scrape():
    CrawlStateSingleton.get_instance().save(override=True)
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
