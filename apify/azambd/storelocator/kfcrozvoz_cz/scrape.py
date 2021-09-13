import time
import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "kfcrozvoz.cz"
website = "https://kfc.cz"
page_url = f"{website}/main/home/restaurants"
json_url = "https://kfcrozvoz.cz/ordering-api/rest/v2/restaurants/"
MISSING = SgRecord.MISSING

headers = {
    "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
    "Accept-Language": "cs",
    "sec-ch-ua-mobile": "?0",
    "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NTk1MTQ2NTc2MjMsXCJhY2NvdW50Tm9uTG9ja2VkXCI6dHJ1ZSxcImNyZWRlbnRpYWxzTm9uRXhwaXJlZFwiOnRydWUsXCJhY2NvdW50Tm9uRXhwaXJlZFwiOnRydWUsXCJlbmFibGVkXCI6dHJ1ZX0ifQ.9uSOyMgJbYz5cNPBH-DuWHn28Krhmp3iotbiCKqQszY8xvCeA9MWoY-GObx1G9rI07GfmIVAs_Bas73VYY3qZA",
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kfc.cz/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Brand": "KFC",
}

headers2 = {
    "sec-ch-ua": '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
    "Accept-Language": "cs",
    "sec-ch-ua-mobile": "?0",
    "Authorization": "Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJ7XCJkZXZpY2VVdWlkXCI6XCJGRkZGRkZGRi1GRkZGLUZGRkYtRkZGRi1GRkZGRkZGRkZGRkZcIixcImRldmljZVV1aWRTb3VyY2VcIjpcIkZJTkdFUlBSSU5UXCIsXCJpbXBsVmVyc2lvblwiOlwiMy4wXCIsXCJzb3VyY2VcIjpcIldFQl9LRkNcIixcImV4cGlyaWF0aW9uRGF0ZVwiOjE2NTk1MTQ2NTc2MjMsXCJhY2NvdW50Tm9uTG9ja2VkXCI6dHJ1ZSxcImNyZWRlbnRpYWxzTm9uRXhwaXJlZFwiOnRydWUsXCJhY2NvdW50Tm9uRXhwaXJlZFwiOnRydWUsXCJlbmFibGVkXCI6dHJ1ZX0ifQ.9uSOyMgJbYz5cNPBH-DuWHn28Krhmp3iotbiCKqQszY8xvCeA9MWoY-GObx1G9rI07GfmIVAs_Bas73VYY3qZA",
    "Content-Type": "application/json; charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://kfc.cz/",
    "Source": "WEB",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Brand": "KFC",
    "sec-ch-ua-platform": '"macOS"',
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def get_page(url):
    return session.get(url, headers=headers, data={})


def get_page2(url):
    return session.get(url, headers=headers2, data={})


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


days1 = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_hoo(response):
    hours_of_operation = []
    for index in range(0, len(days)):
        day = days[index]
        day1 = days1[index]
        start = get_JSON_object_variable(response, f"open{day}From")
        stop = get_JSON_object_variable(response, f"open{day}To")
        if start != MISSING and stop != MISSING:
            hours_of_operation.append(f"{day1}: {start} - {stop}")

    hours_of_operation = "; ".join(hours_of_operation)
    return hours_of_operation


def fetch_data():
    response = get_page(json_url)
    body = json.loads(response.text)
    stores = get_JSON_object_variable(body, "restaurants", [])
    log.info(f"Total stores = {len(stores)}")

    count = 0
    for store in stores:
        count = count + 1
        store_number = str(get_JSON_object_variable(store, "id"))
        page_url = f"https://kfc.cz/main/home/restaurant/{store_number}"
        req_url = f"https://kfcrozvoz.cz/ordering-api/rest/v1/restaurants/details/{store_number}"
        log.debug(f"{count}. Crawling {req_url} ...")
        response = get_page2(req_url)
        body = json.loads(response.text)["details"]
        location_type = MISSING
        state = MISSING
        country_code = "CZ"

        location_name = get_JSON_object_variable(body, "name")
        street_address = get_JSON_object_variable(body, "addressStreetNo")

        if street_address == MISSING:
            street_address = ""
        street_address = (
            street_address + " " + get_JSON_object_variable(body, "addressStreet")
        )
        street_address = street_address.strip()

        city = get_JSON_object_variable(body, "addressCity")
        zip_postal = get_JSON_object_variable(body, "addressPostalCode")
        latitude = get_JSON_object_variable(body, "lat")
        longitude = get_JSON_object_variable(body, "lng")
        phone = get_JSON_object_variable(body, "phoneNo")
        hours_of_operation = get_hoo(
            get_JSON_object_variable(body, "facilityOpenHours")
        )
        raw_address = f"{street_address}, {city}, {zip_postal}"

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
    return []


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total Rows Added= {count}")
    log.info(f"Crawling took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
