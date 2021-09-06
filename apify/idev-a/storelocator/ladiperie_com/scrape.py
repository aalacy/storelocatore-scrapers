import re
from lxml import html
import time
import json
from sgpostal.sgpostal import parse_address_intl

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

DOMAIN = "ladiperie.com"
website = "https://ladiperie.com"
MISSING = SgRecord.MISSING

headers = {
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def request_with_retries(url):
    return session.get(url, headers=headers)


def get_jsobject(response, varName, noVal=MISSING):
    JSObject = re.findall(f'{varName} = "(.+?)";', response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def get_google_parent(data, depth=7, string=""):
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


def fix_string(value=MISSING):
    value = (
        value.replace("\\u0026", "&")
        .replace("\\n", "  ")
        .replace("\n", "  ")
        .replace(" Tel:", "")
        .replace("\t", "  ")
        .replace("\\t", "  ")
        .strip()
    )
    if len(value) == 0:
        return MISSING
    return " ".join(value.split())


def get_information_from_google(url):
    response = request_with_retries(url)
    data = (
        get_jsobject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
    )
    data = json.loads(data)
    dataJSONs = get_google_parent(data, 7, '"description"')

    locations = []
    for dataJSON in dataJSONs:
        latitude = dataJSON[1][0][0][0]
        longitude = dataJSON[1][0][0][1]

        name_part = get_google_parent(dataJSON, 2, '"name"')
        description_part = get_google_parent(dataJSON, 2, '"description"')

        locations.append(
            {
                "location_name": fix_string(name_part[1][0]),
                "latitude": latitude,
                "longitude": longitude,
                "description": fix_string(description_part[1][0]),
            }
        )

    log.debug(f"Found {len(locations)} locations from map")

    return locations


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        if " " in phone:
            phone = " ".join(phone.split()[1:])
        return phone
    return phone


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
            if city == MISSING:
                city1 = (
                    raw_address.lower()
                    .replace(street_address.lower(), "")
                    .replace(state.lower(), "")
                    .replace(zip_postal.lower(), "")
                    .replace(",", "")
                    .strip()
                    .split(" (")[0]
                )

                city1 = (
                    city1.replace("-", "").replace(street_address.lower(), "").strip()
                )

                if len(city1) > 2:
                    city = city1.capitalize()
                if len(city1) == 2:
                    state = city1.upper()
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"No Address {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    response = request_with_retries(f"{website}/pages/location-and-hours")
    body = html.fromstring(response.text, "lxml")
    googleUrl = body.xpath('//iframe[contains(@src, "google.com/maps")]/@src')[0]

    stores = get_information_from_google(googleUrl)
    log.info(f"Total stores = {len(stores)}")

    for store in stores:
        store_number = MISSING
        location_type = MISSING
        page_url = website
        country_code = "CA"

        latitude = store["latitude"]
        longitude = store["longitude"]
        description = store["description"]
        location_name = store["location_name"]
        phone = get_phone(description)

        if phone == MISSING:
            if "**" in description:
                raw_address = description.split("**")
                hoo = MISSING
            elif "Mon-" in description:
                raw_address = description.split("Mon-")
                hoo = "Mon-" + raw_address[1]
            else:
                raw_address = description.split("Mon-")
                hoo = MISSING
        else:
            raw_address = description.split(phone)
            hoo = raw_address[1]
        raw_address = raw_address[0].strip()
        street_address, city, state, zip_postal = get_address(raw_address)
        if "*opening soon*" in city:
            city = city.replace("*opening soon*", "").strip()
        hoo = hoo.strip()
        raw_address = raw_address.split(" (")[0]

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
            hours_of_operation=hoo,
            raw_address=raw_address,
        )
    return []


def scrape():
    log.info(f"Start scrapping {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
