import re
from lxml import html
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "https://versacold.com"
MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=website)

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


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


def fixString(value=MISSING):
    value = (
        value.replace("\\u0026", "&").replace("\\n", "  ").replace("\n", "  ").strip()
    )
    if len(value) == 0:
        return MISSING
    return value


def getInformationFromGoogle(url):
    response = request_with_retries(url)
    data = (
        getJSObject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
    )
    data = json.loads(data)
    rootJsons = getGoogleParent(data, 2, '"Name"')
    locations = []

    for rootJson in rootJsons:
        dataJSONs = getGoogleParent(rootJson, 4, '"Name"')

        for dataJSON in dataJSONs:
            latitude = dataJSON[1][0][0][0]
            longitude = dataJSON[1][0][0][1]

            name_part = getGoogleParent(dataJSON, 2, '"Name"')
            location_name = name_part[1][0]
            location_name = fixString(location_name)
            address = fixString(getGoogleParent(dataJSON, 3, '"Address"')[1][0])
            phone = getGoogleParent(dataJSON, 3, '"Phone"')
            if phone is None:
                phone = MISSING
            else:
                phone = fixString(phone[1][0])

            hoo = []
            for day in days:
                data = getGoogleParent(dataJSON, 3, '"' + day + '"')
                if data is not None:
                    hoo.append(day + ": " + fixString(data[1][0]))
            hoo = "; ".join(hoo)
            locations.append(
                {
                    "location_name": location_name,
                    "hoo": hoo,
                    "phone": phone,
                    "address": address,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            )

    log.debug(f"Found {len(locations)} locations from map")

    return locations


def getAddress(raw_address):
    parts = raw_address.split()
    zip_postal = parts[len(parts) - 2] + " " + parts[len(parts) - 1]

    address = raw_address.replace(zip_postal, "").strip()
    parts1 = address.split(",")
    state = parts1[len(parts1) - 1].strip()
    address = address.replace(", " + state, "").replace(",  " + state, "").strip()

    if "  " in address:
        parts = address.split("  ")
        city = parts[len(parts) - 1].strip()
        street_address = address.replace(city, "").strip()
    else:
        parts = address.split(", ")
        city = parts[len(parts) - 1].strip()
        street_address = address.replace(", " + city, "").strip()

    if "," in city:
        city = city.split(",")[0]
    return street_address, city, state, zip_postal


def fetchData():
    response = request_with_retries(website)
    body = html.fromstring(response.text, "lxml")

    googleUrl = body.xpath('//iframe[contains(@src, "google.com/maps")]/@src')[0]

    stores = getInformationFromGoogle(googleUrl)
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        store_number = MISSING
        location_type = MISSING
        page_url = website

        location_name = store["location_name"]
        street_address, city, state, zip_postal = getAddress(store["address"])
        raw_address = f"{street_address}, {city}, {state} {zip_postal}"
        country_code = "CA"
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        hours_of_operation = store["hoo"]

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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
