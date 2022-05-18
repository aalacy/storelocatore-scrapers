from lxml import html
import re
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

website = "englishcolor.com"
MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def request_with_retries(url):
    return session.get(url, headers=headers)


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def getGoogleParent(data, depth=7, string=""):
    count = 0
    while True:
        result = None
        for singleData in data:
            if string in json.dumps(singleData):
                result = singleData
                break
        if result is None:
            return None
        data = singleData
        count = count + 1
        if count == depth:
            return singleData


def getPhone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def getInformationFromGoogle(url):
    response = request_with_retries(url)
    data = (
        getJSObject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
    )

    data = json.loads(data)
    rootJsons = getGoogleParent(data, 2, '"name"')
    locations = []

    for rootJson in rootJsons:
        dataJSONs = getGoogleParent(rootJson, 4, '"name"')

        for dataJSON in dataJSONs:
            latitude = dataJSON[1][0][0][0]
            longitude = dataJSON[1][0][0][1]

            name_part = getGoogleParent(dataJSON, 2, '"name"')
            location_name = name_part[1][0]
            location_name = (
                location_name.replace("\\u0026", "&")
                .replace("\\n", " ")
                .replace("\n", " ")
                .strip()
            )
            locations.append(
                {
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "Found": 0,
                }
            )

    log.info(f"Found {len(locations)} locations from map")

    return locations


def fetchStores():
    response = request_with_retries("http://www.englishcolor.com/locations/")
    body = html.fromstring(response.text, "lxml")

    googleUrl = body.xpath('//iframe[contains(@src, "google.com/maps")]/@src')[0]

    googleLocations = getInformationFromGoogle(googleUrl)

    menuUrls = body.xpath('//ul[contains(@id, "menu-locations")]/li/a/@href')
    log.info(f"Total menu locations = {len(menuUrls)}")
    stores = []

    count = 0
    for menuUrl in menuUrls:
        count = count + 1
        response = request_with_retries(menuUrl)
        body = html.fromstring(response.text, "lxml")
        mainDivs = body.xpath("//div[contains(@class, 'fusion-column-wrapper')]")
        cityCount = 0
        for mainDiv in mainDivs:
            directions = mainDiv.xpath(".//a[text()='Directions']") + mainDiv.xpath(
                ".//span[text()='Directions']"
            )
            if len(directions) == 0:
                continue
            title = mainDiv.xpath(".//h1/text()")[0]
            spans = mainDiv.xpath(".//span/text()")
            texts = []
            for span in spans:
                span = span.replace("\n", "").strip()
                if len(span) > 0:
                    texts.append(span)

            allTxt = ", ".join(texts)
            phone = getPhone(allTxt)

            address, hoo = allTxt.split("Hours:")
            address = address.replace(phone, "").replace(",,", ",").strip()
            if address[-1] == ",":
                address = address[:-1]
            hoo = hoo.replace(", Directions", "").strip()

            cityCount = cityCount + 1
            stores.append(
                {
                    "title": title,
                    "address": address,
                    "phone": phone,
                    "hoo": hoo,
                    "latitude": MISSING,
                    "longitude": MISSING,
                    "page_url": menuUrl,
                    "location_name": title,
                }
            )
        log.info(f"{count}. Scrapped {menuUrl} total store = {cityCount}")

    for storeIndex in range(0, len(stores)):
        store = stores[storeIndex]
        Found = False
        for index in range(0, len(googleLocations)):
            location = googleLocations[index]
            if (
                location["Found"] == 0
                and store["title"].lower() in location["location_name"].lower()
            ):
                Found = index
                break

            if Found is False:
                for index in range(0, len(googleLocations)):
                    location = googleLocations[index]
                    if (
                        location["Found"] == 0
                        and location["location_name"]
                        .replace("English Color & Supply", "")
                        .lower()
                        .strip()
                        in store["address"].lower()
                    ):
                        Found = index
                        break

            if Found is False:
                for index in range(0, len(googleLocations)):
                    location = googleLocations[index]
                    if (
                        location["location_name"]
                        .replace("English Color & Supply", "")
                        .lower()
                        .strip()
                        in store["address"].lower()
                    ):
                        Found = index
                        break

        if Found is not False:
            googleLocations[Found]["Found"] = googleLocations[Found]["Found"] + 1
            location = googleLocations[Found]

            stores[storeIndex]["location_name"] = location["location_name"]
            stores[storeIndex]["latitude"] = location["latitude"]
            stores[storeIndex]["longitude"] = location["longitude"]

    for storeIndex in range(0, len(stores)):
        store = stores[storeIndex]
        if store["latitude"] != MISSING:
            continue
        Found = False
        for index in range(0, len(googleLocations)):
            location = googleLocations[index]
            if location["Found"] != 0:
                continue
            if "Mobile" in location["location_name"] and "MOBILE" in store["title"]:
                stores[storeIndex]["location_name"] = location["location_name"]
                stores[storeIndex]["latitude"] = location["latitude"]
                stores[storeIndex]["longitude"] = location["longitude"]
                googleLocations[index]["Found"] = 1

            if (
                "MADISON" in location["location_name"].upper()
                and "MONTGOMERY" in store["title"].upper()
            ):
                stores[storeIndex]["location_name"] = location["location_name"]
                stores[storeIndex]["latitude"] = location["latitude"]
                stores[storeIndex]["longitude"] = location["longitude"]
                googleLocations[index]["Found"] = 1

            if (
                "HOUSTON" in location["location_name"].upper()
                and "MONTGOMERY" in store["title"].upper()
            ):
                log.info(location["latitude"])
                stores[storeIndex]["location_name"] = location["location_name"]
                stores[storeIndex]["latitude"] = location["latitude"]
                stores[storeIndex]["longitude"] = location["longitude"]
                googleLocations[index]["Found"] = 1
        if stores[storeIndex]["latitude"] == MISSING:
            for index in range(0, len(googleLocations)):
                location = googleLocations[index]
                if (
                    "HOUSTON" in location["location_name"].upper()
                    and "MONTGOMERY" in store["title"].upper()
                ):
                    log.info(location["latitude"])
                    stores[storeIndex]["location_name"] = location["location_name"]
                    stores[storeIndex]["latitude"] = location["latitude"]
                    stores[storeIndex]["longitude"] = location["longitude"]
                    googleLocations[index]["Found"] = 1
                    break
    return stores


def getAddress(raw_address):
    parts = []

    for part in raw_address.split(","):
        if len(part.strip()) > 0:
            parts.append(part.strip())

    lastPart = parts[len(parts) - 1].split()
    if len(lastPart) == 1:
        zip_postal = parts[len(parts) - 1]
        state = parts[len(parts) - 2]
        city = parts[len(parts) - 3]

        street_address = ""
        for index in range(len(parts) - 3):
            street_address = street_address + " " + parts[index]
    else:
        zip_postal = lastPart[1]
        state = lastPart[0]
        city = parts[len(parts) - 2]

        street_address = ""
        for index in range(len(parts) - 2):
            street_address = street_address + " " + parts[index]

    return street_address, city, state, zip_postal


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        store_number = MISSING
        location_type = MISSING
        page_url = store["page_url"]
        location_name = store["location_name"]
        street_address, city, state, zip_postal = getAddress(store["address"])
        if state.isnumeric():
            street_address = store["address"]
            city = MISSING
            state = MISSING
            zip_postal = MISSING

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

        # Known issue, map does not have info
        if "59 Maple" in str(raw_address):
            city = "Cartersville"
            state = "GA"
            zip_postal = "30120"
            raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
                MISSING, ""
            )

        country_code = "US"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = store["hoo"]
        if longitude == MISSING or longitude == MISSING:
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
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetchData()
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.RAW_ADDRESS,
                }
            )
        )
    ) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
