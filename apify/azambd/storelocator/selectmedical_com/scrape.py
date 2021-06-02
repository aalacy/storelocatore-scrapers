import math
from concurrent.futures import ThreadPoolExecutor
from sgscrape.sgpostal import parse_address_intl
import time
import json
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "selectmedical.com"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)

days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
max_workers = 24


def fetchConcurrentSingle(data):
    store = data["store"]
    url = data["url"]
    if website not in url:
        return store, MISSING

    try:
        response = request_with_retries(url).text
        if "hours" not in response.lower() or "day" not in response.lower():
            return store, MISSING
        hoo = []
        body = html.fromstring(response, "lxml")
    except Exception as e:
        log.error(f"Can't get {url} error:{e}")
        return store, MISSING

    tds = body.xpath("//td/text()")
    tdLen = len(tds) - 2
    for index in range(0, tdLen):
        val = tds[index].strip()
        for day in days:
            if day + ":" in val.lower():
                val1 = tds[index + 1].strip()
                hoo.append(val + " " + val1)

            elif day in val.lower():
                val1 = tds[index + 1].strip()
                hoo.append(val + ": " + val1)

    if len(hoo) == 0:
        return store, MISSING
    return store, "; ".join(hoo)


def fetchConcurrentList(list, occurrence=max_workers):
    output = []
    total = len(list)
    reminder = math.floor(total / 50)
    if reminder < occurrence:
        reminder = occurrence

    count = 0
    with ThreadPoolExecutor(
        max_workers=occurrence, thread_name_prefix="fetcher"
    ) as executor:
        for result in executor.map(fetchConcurrentSingle, list):
            count = count + 1
            if count % reminder == 0:
                log.debug(f"Concurrent Operation count = {count}")
            output.append(result)
    return output


def getAddress(raw_address):
    try:
        if raw_address is not None and raw_address != MISSING:
            data = parse_address_intl(raw_address)
            street_address = data.street_address_1
            city = MISSING
            state = MISSING
            postcode = MISSING

            if data.street_address_2 is not None:
                street_address = street_address + " " + data.street_address_2

            return street_address, data.city, data.state, data.postcode
    except Exception as e:
        log.error(f"getAddress error:{e}")
        pass
    return MISSING, city, state, postcode


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def getJSONObjectVariable(Object, varNames, noVal=MISSING):
    value = noVal
    for varName in varNames.split("."):
        varName = getVarName(varName)
        try:
            value = Object[varName]
            Object = Object[varName]
        except Exception:
            return noVal
    return value


def request_with_retries(url):
    return session.get(url, headers=headers)


def getBodyText(body, path):
    data = body.xpath(path)
    if len(data) == 0:
        return MISSING
    return data[0].strip()


def getBaseInfo(store):
    response = getJSONObjectVariable(store, "Html", MISSING)
    body = html.fromstring(response, "lxml")

    page_url = getBodyText(
        body, '//span[contains(@class, "location-title field-link")]/a/@href'
    )

    location_name = getBodyText(
        body, '//span[contains(@class, "location-title field-link")]/a/text()'
    )

    location_type = getBodyText(
        body, '//div[contains(@class, "line-of-business")]/text()'
    )

    phone = getBodyText(body, '//div[contains(@class, "phone-line")]/a/text()')

    raw_address = (
        getBodyText(body, '//div[contains(@class, "address-line")]/text()')
        .replace("  ", " ")
        .strip()
    )
    street_address, city, state, postcode = getAddress(raw_address)

    store_number = str(getJSONObjectVariable(store, "Id", MISSING))
    latitude = str(getJSONObjectVariable(store, "Geospatial.Latitude", MISSING))
    longitude = str(getJSONObjectVariable(store, "Geospatial.Longitude", MISSING))
    return page_url, {
        "store_number": store_number,
        "page_url": page_url,
        "location_name": location_name,
        "location_type": location_type,
        "phone": phone,
        "raw_address": raw_address,
        "street_address": street_address,
        "city": city,
        "state": state,
        "zip_postal": postcode,
        "latitude": latitude,
        "longitude": longitude,
    }


def fetchStores():
    response = request_with_retries(
        "https://www.selectmedical.com//sxa/search/results/?s={648F4C3A-C9EA-4FCF-82A3-39ED2AC90A06}&itemid={94793D6A-7CC7-4A8E-AF41-2FB3EC154E1C}&sig=&autoFireSearch=true&v={D2D3D65E-3A18-43DD-890F-1328E992446A}&p=500000&e=0&g=&o=Distance,Ascending"
    )
    data = json.loads(response.text.replace("<br />", ", ").replace("<br/>", ", "))
    stores = []
    failedStores = []

    for store in getJSONObjectVariable(data, "Results", []):
        url, store = getBaseInfo(store)
        if url and store["location_name"] == MISSING:
            failedStores.append(store)
            log.error(
                f"{len(failedStores)}. url is missing for=> {store['store_number']} : {store['location_name']}"
            )
        else:
            stores.append(
                {
                    "store": store,
                    "url": url,
                }
            )
    log.error(f"Url is missing for {len(failedStores)} stores")

    return stores


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    stores = stores
    for store, hours_of_operation in fetchConcurrentList(stores):
        store_number = store["store_number"]
        page_url = store["page_url"]
        location_name = store["location_name"]
        location_type = store["location_type"]
        street_address = store["street_address"]
        city = store["city"]
        zip_postal = store["zip_postal"]
        state = store["state"]
        country_code = "US"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        raw_address = store["raw_address"]
        if latitude and longitude is None:
            continue

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
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
