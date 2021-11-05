import math
from concurrent.futures import ThreadPoolExecutor
import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "sonicdrivein.com"
website = "https://www.sonicdrivein.com"
json_url = "https://maps.locations.sonicdrivein.com/api/getAsyncLocations?template=search&level=search&search="
MISSING = SgRecord.MISSING
max_workers = 4

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_concurrent_single(zip, tried=0):
    try:
        response = request_with_retries(f"{json_url}{zip}")
        response = json.loads(response.text)
        data = json.loads(
            "["
            + response["maplist"]
            .replace('<div class="tlsmap_list">', "")
            .replace(",</div>", "")
            + "]"
        )
        return zip, data
    except Exception as e:
        if tried == 4:
            log.debug(f"Error in {zip} : {e}")
            return zip, []
        return fetch_concurrent_single(zip, tried + 1)


def fetch_concurrent_list(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for zip, data in executor.map(fetch_concurrent_single, list):
            count = count + 1
            if count % reminder == 0:
                log.debug(f"Concurrent Operation count = {count}")
            log.debug(f"{count}. {zip}  stores = {len(data)}")
            output = output + data
    return output


def request_with_retries(url):
    return session.get(url, headers=headers)


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


def get_hoo(store):
    hoo = None
    try:
        hoo = get_JSON_object_variable(store, "hours_sets:primary")
        hoo = get_JSON_object_variable(json.loads(hoo), "days")
        hours_of_operation = []
        for key in hoo.keys():
            try:
                hours_of_operation.append(
                    f"{key}: {hoo[key][0]['open']} - {hoo[key][0]['close']}"
                )
            except:
                pass

            try:
                hours_of_operation.append(f"{key}: {hoo[key]}")
            except:
                pass
        return "; ".join(hours_of_operation)
    except Exception as e:
        log.info(f"error in hoo: {hoo}, {e}")
        return MISSING


def fetch_data():
    search = DynamicZipSearch(country_codes=[SearchableCountries.USA])

    count = 0
    totalStores = 0
    page_urls = []
    zip_codes = []
    for zip_code in search:
        zip_codes.append(zip_code)
    log.info(f"total zip codes = {len(zip_codes)}")

    for store in fetch_concurrent_list(zip_codes):
        location_type = "Restaurant"
        store_number = get_JSON_object_variable(store, "lid")
        latitude = get_JSON_object_variable(store, "lat")
        longitude = get_JSON_object_variable(store, "lng")
        page_url = get_JSON_object_variable(store, "url")
        location_name = get_JSON_object_variable(store, "location_name")
        street_address = (
            get_JSON_object_variable(store, "address_1")
            + " "
            + get_JSON_object_variable(store, "address_2")
        )
        city = get_JSON_object_variable(store, "city")
        zip_postal = get_JSON_object_variable(store, "post_code")
        state = get_JSON_object_variable(store, "region")
        country_code = get_JSON_object_variable(store, "country")
        phone = get_JSON_object_variable(store, "local_phone")
        hours_of_operation = get_hoo(store)
        log.info(hours_of_operation)
        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]
        if page_url == MISSING:
            log.info(f"store: {store}")
            continue
        if page_url in page_urls:
            continue
        page_urls.append(page_url)
        totalStores = totalStores + 1

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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
