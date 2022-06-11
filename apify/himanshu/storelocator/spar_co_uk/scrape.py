import re
import math
import json
import time
from concurrent.futures import ThreadPoolExecutor
from lxml import html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from bs4 import BeautifulSoup as bs

DOMAIN = "spar.co.uk"

website = "https://www.spar.co.uk"
MISSING = "<MISSING>"
locationUrlFormat = "https://www.spar.co.uk/umbraco/api/storesearch/searchstores?maxResults=5&radius=10&startNodeId=1053&location=&filters=&lat={}&lng={}&filtermethod="


log = sglog.SgLogSetup().get_logger(logger_name=website)

max_workers = 24
headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
}


def fetchConcurrentSingle(data):
    response = request_with_retries(data["url"])
    return {"data": data, "response": response.text}


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


def getVarName(value):
    try:
        return int(value)
    except ValueError:
        pass
    return value


def isEmptyString(value):
    if value is None:
        return True
    if MISSING == value:
        return True
    value = value.strip()
    return len(value) == 0


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


def getPhone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def request_with_retries(url):
    with SgRequests() as session:
        return session.get(url, headers=headers)


def fetchStores():
    all_coords = DynamicGeoSearch(country_codes=[SearchableCountries.BRITAIN])
    locationUrls = []
    for lat, lng in all_coords:
        locationUrls.append({"url": locationUrlFormat.format(lat, lng)})
    log.info(f"Total coordinates = {len(locationUrls)}")

    urls = []
    stores = []
    for result in fetchConcurrentList(locationUrls):
        jsonData = json.loads(result["response"])

        locations = getJSONObjectVariable(jsonData, "locations", [])
        if locations is None:
            continue
        for location in locations:
            if location["url"] in urls:
                continue
            urls.append(location["url"])
            latitude = getJSONObjectVariable(location, "lat")
            longitude = getJSONObjectVariable(location, "lng")
            all_coords.found_location_at(latitude, longitude)

            page_url = f"{website}{location['url']}"
            log.info(page_url)
            try:
                services = list(
                    bs(request_with_retries(page_url).text, "lxml")
                    .select_one("ul.store-services__list")
                    .stripped_strings
                )
            except:
                pass

            stores.append(
                {
                    "url": page_url,
                    "location_name": getJSONObjectVariable(location, "name")
                    .replace("\t", " ")
                    .strip(),
                    "phone": getPhone(getJSONObjectVariable(location, "telephone")),
                    "latitude": latitude,
                    "longitude": longitude,
                    "services": ", ".join(services),
                    "store_number": getJSONObjectVariable(location, "code")
                    .replace("\t", " ")
                    .strip(),
                }
            )
    return stores


def getHoo(jsonData=[]):
    Object = None
    for data in jsonData:
        if "openingHoursSpecification" in data:
            Object = data
    if Object is None:
        return MISSING
    locData = json.loads(Object)
    specif = getJSONObjectVariable(locData, "openingHoursSpecification")

    if specif is None or specif is MISSING:
        return MISSING
    hoo = []
    for element in specif:
        day = element["dayOfWeek"][0]
        opens = element["opens"]
        closes = element["closes"]
        hoo.append(f"{day} {opens} {closes}")
    hoo = [e.strip() for e in hoo if e.strip()]
    return " ".join(hoo) if hoo else MISSING


def getAddress(body):
    ps = body.xpath('//div[contains(@class, "store-details__contact")]/p')
    address = []
    phone = body.xpath('//div[contains(@class, "store-details__contact")]/p/a/text()')
    if len(phone) > 0:
        phone = phone[0].strip()
    else:
        phone = MISSING
    for p in ps:
        node = (
            (" ".join(p.itertext()))
            .replace("\r", "")
            .replace("\n", "")
            .replace("\t", "")
            .replace(phone, "")
            .strip()
        )
        node = re.sub(" +", " ", node).strip()
        node = node.replace(" ,", ",").replace(", ", ",")
        node = ", ".join(node.split(",")).strip()
        if not isEmptyString(node) and node != ",":
            address.append(node)
    raw_address = " ".join(address).replace(" ,", ",").strip()
    if raw_address.count(", ") < 1:
        return raw_address, MISSING, MISSING, MISSING

    data = raw_address.split(", ")
    if raw_address.count(", ") == 1:
        return raw_address, data[0], MISSING, data[1]

    city = data[len(data) - 2]
    zip_postal = data[len(data) - 1]
    street_address = raw_address.replace(f", {city}, {zip_postal}", "")
    if isEmptyString(city):
        city = MISSING
    if isEmptyString(zip_postal):
        zip_postal = MISSING
    if isEmptyString(street_address):
        street_address = MISSING
    return raw_address, street_address, city, zip_postal


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for result in fetchConcurrentList(stores):
        data = result["data"]
        response = result["response"]

        body = html.fromstring(response, "lxml")
        jsonData = body.xpath('//script[contains(text(), "postalCode")]/text()')

        store_number = data["store_number"]
        page_url = data["url"]
        location_name = data["location_name"]
        phone = data["phone"]
        latitude = data["latitude"]
        longitude = data["longitude"]
        raw_address, street_address, city, zip_postal = getAddress(body)

        country_code = "UK"
        hours_of_operation = getHoo(jsonData)

        yield SgRecord(
            locator_domain=DOMAIN,
            store_number=store_number,
            page_url=page_url,
            location_name=location_name,
            location_type=data["services"],
            street_address=street_address,
            city=city,
            zip_postal=zip_postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=100
        )
    ) as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total row added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
