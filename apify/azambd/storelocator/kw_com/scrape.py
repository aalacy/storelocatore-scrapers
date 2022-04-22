import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgpostal.sgpostal import parse_address_intl

DOMAIN = "kw.com"
website = "https://www.kw.com"
json_url = "https://api-endpoint.cons-prod-us-central1.kw.com/graphql"
MISSING = SgRecord.MISSING

headers = {
    "authority": "api-endpoint.cons-prod-us-central1.kw.com",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "authorization": "",
    "content-type": "application/json",
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "x-shared-secret": "MjFydHQ0dndjM3ZAI0ZHQCQkI0BHIyM=",
    "sec-ch-ua-platform": '"macOS"',
    "origin": "https://www.kw.com",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.kw.com/",
    "accept-language": "en-US,en;q=0.9,bn;q=0.8",
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_stores():
    data = json.dumps(
        {
            "operationName": None,
            "variables": {},
            "query": "{\n  ListOfficeQuery {\n    id\n    name\n    address\n    subAddress\n    phone\n    fax\n    lat\n    lng\n    url\n    contacts {\n      name\n      email\n      phone\n      __typename\n    }\n    __typename\n  }\n}\n",
        }
    )
    response = session.post(json_url, headers=headers, data=data)
    return json.loads(response.text)["data"]["ListOfficeQuery"]


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
        log.info(f"Address Err: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


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

    if value is None:
        return noVal
    return value


def fetch_data():
    stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        location_type = MISSING
        hours_of_operation = MISSING
        country_code = "US"
        store_number = str(get_JSON_object_variable(store, "id"))
        location_name = str(get_JSON_object_variable(store, "name"))
        raw_address = (
            str(get_JSON_object_variable(store, "address"))
            + " "
            + str(get_JSON_object_variable(store, "subAddress"))
        )
        raw_address = raw_address.replace(MISSING, " ").strip()
        street_address, city, state, zip_postal = get_address(raw_address)
        phone = str(get_JSON_object_variable(store, "phone"))
        latitude = str(get_JSON_object_variable(store, "lat"))
        longitude = str(get_JSON_object_variable(store, "lng"))
        page_url = str(get_JSON_object_variable(store, "url"))
        raw_address = raw_address

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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
