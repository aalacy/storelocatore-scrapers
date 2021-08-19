from sgscrape.sgpostal import parse_address_intl
from lxml import html
import re
import time
import json

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "https://www.cnbb.bank"
MISSING = "<MISSING>"

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests().requests_retry_session()
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


def getInformationFromGoogle(url):
    log.info(f"Called getInformationFromGoogle : {url}")
    response = request_with_retries(url)
    data = (
        getJSObject(response.text, "_pageData")
        .replace("null", '"null"')
        .replace('\\"', '"')
    )

    data = json.loads(data)
    dataJSONs = getGoogleParent(data, 7, '"description"')

    locations = []
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
        if "ATM" in description:
            location_type = "ATM"
        else:
            location_type = "Branch and ATM"
        locations.append(
            {
                "location_name": location_name,
                "latitude": latitude,
                "longitude": longitude,
                "description": description,
                "location_type": location_type,
            }
        )

    log.debug(f"Found {len(locations)} locations from map")

    return locations


def getUrlLocations(urls):
    count = 0
    locations = []
    atms = []

    for page_url in urls:
        count = count + 1
        page_url = f"{website}{page_url}"
        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")
        h3s = body.xpath('//div[@class="liveaccdefault"]/div/h3/a')
        log.debug(f"{count}. Total store in {page_url} is {len(h3s)}")

        for h3 in h3s:
            location_name = h3.xpath(".//text()")[0]
            name = h3.xpath(".//@name")[0]

            attributes = body.xpath(f'//div[@id="{name}"]/div[@class="col3"]')
            phone = attributes[1].xpath(".//p/text()")[0].replace("Phone:", "").strip()

            values = attributes[0].xpath(".//p/text()")

            address = []
            hoo = []
            for value in values:
                value = (
                    value.replace("<br />", " ")
                    .replace("\\n", " ")
                    .replace("\n", " ")
                    .strip()
                )
                value = " ".join(value.split())
                if "0am" in value or "0pm" in value:
                    hoo.append(value)
                else:
                    address.append(value)

            address = ", ".join(address)
            hoo = ", ".join(hoo)

            if len(hoo) == 0:
                hoo = MISSING

            if len(phone) == 0:
                phone = MISSING

            locations.append(
                {
                    "location_name": location_name,
                    "page_url": page_url,
                    "phone": phone,
                    "raw_address": address,
                    "hoo": hoo,
                }
            )

        atmDiv = body.xpath("//div[@class='locationATMs']")[0]
        for a in atmDiv.xpath(".//a"):
            atms.append(
                {
                    "name": a.xpath(".//text()")[0],
                    "href": a.xpath(".//@href")[0],
                    "page_url": page_url,
                }
            )

    log.debug(f"Total locations from pages ={len(locations)}")
    log.debug(f"Total atms from pages ={len(atms)}")
    return locations, atms


def fetchStores():
    response = request_with_retries(f"{website}/About-CNB/Locations")
    body = html.fromstring(response.text, "lxml")
    googleUrl = body.xpath('//iframe[contains(@src, "google.com/maps")]/@src')[0]

    googleLocations = getInformationFromGoogle(googleUrl)
    locations, atms = getUrlLocations(body.xpath('//a[@class="btnMore"]/@href'))

    stores = []
    for googleLocation in googleLocations:
        Found = False
        for location in locations:
            if (
                googleLocation["location_name"] in location["location_name"]
                or location["phone"] in googleLocation["description"]
            ):
                Found = True
                hoo = location["hoo"]
                if hoo == MISSING:
                    hoo = googleLocation["description"].split("Lobby")
                    if len(hoo) > 1:
                        hoo = hoo[1].replace("\\n", "").replace("\n", "").strip()
                stores.append(
                    {
                        "location_name": googleLocation["location_name"],
                        "page_url": location["page_url"],
                        "phone": location["phone"],
                        "raw_address": location["raw_address"],
                        "latitude": googleLocation["latitude"],
                        "longitude": googleLocation["longitude"],
                        "hoo": hoo,
                        "location_type": googleLocation["location_type"],
                    }
                )
        if Found is False:
            foundAtm = False
            for atm in atms:
                if googleLocation["location_name"] in atm["name"]:
                    foundAtm = atm

            if foundAtm is not False:
                log.debug(
                    f'{googleLocation["location_name"]} retrieve address {foundAtm["href"]} ...'
                )
                response = request_with_retries(foundAtm["href"])
                body = html.fromstring(response.text, "lxml")
                raw_address = body.xpath("//meta[@itemprop='name']/@content")

                if len(raw_address) == 0:
                    raw_address = MISSING
                else:
                    raw_address = raw_address[0].split(".")
                    raw_address = raw_address[len(raw_address) - 1].strip()

                stores.append(
                    {
                        "location_name": googleLocation["location_name"],
                        "page_url": foundAtm["page_url"],
                        "phone": MISSING,
                        "raw_address": raw_address,
                        "latitude": googleLocation["latitude"],
                        "longitude": googleLocation["longitude"],
                        "hoo": MISSING,
                        "location_type": googleLocation["location_type"],
                    }
                )
    return stores


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
        log.info(f"Invalid Address: {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    for store in stores:
        store_number = MISSING
        location_type = store["location_type"]
        page_url = store["page_url"]
        location_name = store["location_name"]

        raw_address = store["raw_address"]
        street_address, city, state, zip_postal = getAddress(raw_address)
        raw_address = f"{street_address}, {city}, {state} {zip_postal}"
        country_code = "US"
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
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
