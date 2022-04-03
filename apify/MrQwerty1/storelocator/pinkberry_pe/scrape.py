import re
import time
import json
from sgpostal.sgpostal import parse_address_intl
from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

import ssl

ssl._create_default_https_context = ssl._create_unverified_context

locator_domain = "pinkberry.pe"
website = "http://www.pinkberry.pe"
map_url = "https://www.google.com/maps/dir//{},{}/@{},{}z"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def getPage(url):
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
    response = getPage(url)

    data = (
        getJSObject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
    )
    data = json.loads(data)

    dataJSONs = getGoogleParent(data, 2, '"Nombre"')

    locations = []
    for dataJSONc in dataJSONs[2:]:
        for dataJSON in dataJSONc[4]:
            latitude = dataJSON[4][4][0]

            longitude = dataJSON[4][4][1]

            location_name = dataJSON[5][0][0]
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
                }
            )

    log.debug(f"Found {len(locations)} locations from map")

    return locations


def getAddress(raw_address):
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
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetchData():
    with SgChrome(user_agent=user_agent) as driver:
        googleUrl = "https://www.google.com/maps/d/u/0/embed?mid=10hwvufd2OppSAvtr07s7tBBxF6H_Vhjd&ll=-12.079721680392199%2C-76.96960150000001&z=14"
        stores = getInformationFromGoogle(googleUrl)
        log.info(f"Total stores = {len(stores)}")
        x = 0
        for store in stores:
            x = x + 1
            store_number = MISSING
            location_type = MISSING
            page_url = "https://www.pinkberry.pe/estatico/zonasreparto"

            location_name = store["location_name"]
            log.info(f"Pulling info:Location#{x}. {location_name}")
            country_code = "PE"
            phone = MISSING
            latitude = store["latitude"]
            longitude = store["longitude"]
            hours_of_operation = MISSING

            driver.get(map_url.format(latitude, longitude, latitude, longitude))
            time.sleep(30)
            htmlSource = driver.page_source
            sp1 = bs(htmlSource, "html.parser")
            addr = (
                sp1.select("input.tactile-searchbox-input")[-1]["aria-label"]
                .replace("Destination", "")
                .strip()
            )
            street_address, city, state, zip_postal = getAddress(addr)
            if " " in zip_postal:
                zip_postal = zip_postal.split()[-1]
            raw_address = f"{addr}"

            yield SgRecord(
                locator_domain=locator_domain,
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
    log.info(f"Start Crawling {locator_domain} ...")
    start = time.time()
    result = fetchData()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end - start} seconds.")


if __name__ == "__main__":
    scrape()
