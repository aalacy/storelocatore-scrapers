from lxml import html
import re
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "ddlebanon.com"
website = "https://ddlebanon.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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


def getInformationFromGoogle(url):
    response = request_with_retries(url)
    data = (
        getJSObject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
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
            description_part = getGoogleParent(dataJSON, 2, '"description"')
            description = description_part[1][0]
            description = (
                description.replace("\\u0026", "&")
                .replace("\\n", " ")
                .replace("\n", " ")
                .strip()
            )
            locations.append(
                {
                    "location_name": location_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "description": description,
                }
            )

    log.debug(f"Found {len(locations)} locations from map")

    return locations


def fetchStores():
    response = request_with_retries(f"{website}/index.php/contact-us")
    body = html.fromstring(response.text, "lxml")

    googleUrl = body.xpath('//iframe[contains(@src, "google.com/maps")]/@src')[0]

    return getInformationFromGoogle(googleUrl)


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        location_name = store["location_name"]
        latitude = store["latitude"]
        longitude = store["longitude"]
        description = store["description"]

        if description in location_name:
            city = description
            street_address = MISSING
        else:
            city = description.split(",")[len(description.split(",")) - 1]
            street_address = description.replace("," + city, "")
            city = city.split("–")[0].strip()

        page_url = f"{website}/index.php/contact-us"
        country_code = "LB"

        store_number = MISSING
        location_type = MISSING
        zip_postal = MISSING
        state = MISSING
        raw_address = MISSING
        phone = MISSING
        hours_of_operation = MISSING

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
