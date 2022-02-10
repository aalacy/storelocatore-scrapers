from lxml import html
import time
import json
from concurrent.futures import ThreadPoolExecutor

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://www.smartstyle.com"
starter_url = f"{website}/en-us/salon-directory.html"
json_url = "https://info3.regiscorp.com/salonservices/siteid/6/salon/"
MISSING = SgRecord.MISSING
max_workers = 10

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url, retry=1):
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 404:
            log.error(f"failed with status code ={response.status_code}")
            return None
        if response.status_code == 200:
            return html.fromstring(response.text, "lxml")
        else:
            log.error(f"failed with status code ={response.status_code}")
    except Exception as e:
        log.error(f"Failed to load e={e}")
    if retry > 3:
        return None
    return request_with_retries(url, retry + 1)


def fetch_store(page_url):
    store_number = page_url.replace(".html", "").split("-")
    store_number = store_number[len(store_number) - 1]
    response = session.get(json_url + store_number, headers=headers)
    if response.status_code == 200:
        return page_url, store_number, json.loads(response.text)
    return page_url, None, None


def fetch_stores():
    body = request_with_retries(starter_url)
    codeNames = ["US", "CA", "PR"]
    codes = {}
    countries = body.xpath('//div[contains(@class, "acs-commons-resp-colctrl-row")]')
    log.info(f"Total countries = {len(countries)}")
    stores = []
    count = 0
    for index in range(0, len(countries)):
        code = codeNames[index]
        cities = countries[index].xpath('.//a[contains(@href, "/locations/")]/@href')
        log.info(f"Total cities = {len(cities)}")

        for city in cities:
            count = count + 1
            body = request_with_retries(city)
            if body is None:
                continue

            newStores = body.xpath('//td/a[contains(@href, "/locations/")]/@href')
            log.info(f"{count}. newStores = {len(newStores)} in {city}")

            for store in newStores:
                store = f"{website}{store}"
                if store not in stores:
                    stores.append(store)
                    codes[store] = code
    return codes, stores


def get_var_name(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def get_JSON_object(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = get_var_name(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return " ".join((" ".join(values)).split())


def get_hoo(page_url, hours_of_operation):
    hoo = []
    for h in hours_of_operation:
        hoo.append(f"{h['days']}:{h['hours']['open']} - {h['hours']['close']}")
    hoo = "; ".join(hoo)
    if len(hoo) > 0:
        return hoo
    body = request_with_retries(page_url)
    if body is None:
        return MISSING
    hoo = stringify_nodes(body, '//div[contains(@class, "store-hours")]')
    return hoo


def fetch_data():
    codes, stores = fetch_stores()
    log.info(f"Total stores = {len(stores)}")

    location_type = MISSING
    with ThreadPoolExecutor(
        max_workers=max_workers, thread_name_prefix="fetcher"
    ) as executor:
        for page_url, store_number, store in executor.map(fetch_store, stores):
            if store_number is None:
                continue
            location_name = get_JSON_object(store, "name")
            street_address = get_JSON_object(store, "address")
            city = get_JSON_object(store, "city")
            state = get_JSON_object(store, "state")
            zip_postal = get_JSON_object(store, "zip")
            location_name = get_JSON_object(store, "name")
            country_code = codes[page_url]
            phone = get_JSON_object(store, "phonenumber")
            latitude = get_JSON_object(store, "latitude")
            longitude = get_JSON_object(store, "longitude")
            hours_of_operation = get_JSON_object(store, "store_hours")

            hours_of_operation = get_hoo(
                page_url, get_JSON_object(store, "store_hours")
            )
            if "0" not in hours_of_operation:
                hours_of_operation = "Temporarily Closed"
            if "Sun" not in hours_of_operation:
                hours_of_operation = hours_of_operation + "; Sun:Closed"
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


def scrape():
    log.info(f"Start crawling {website} ...")
    start = time.time()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
