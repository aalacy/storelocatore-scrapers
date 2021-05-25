import time
import re
from xml.etree import ElementTree as ET
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

website = "https://thaiexpress.ca"
MISSING = "<MISSING>"


session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=website)


def getXMLRoot(text):
    return ET.fromstring(text)


def getXMLObjectVariable(Object, varNames, noVal=MISSING, noText=False):
    Object = [Object]
    for varName in varNames.split("."):
        value = []
        for element in Object[0]:
            if varName == element.tag:
                value.append(element)
        if len(value) == 0:
            return noVal
        Object = value

    if noText is True:
        return Object
    if len(Object) == 0 or Object[0].text is None:
        return MISSING
    return Object[0].text


def getPhone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


def fetchStores():
    response = session.get(
        f"{website}/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    )
    data = getXMLRoot(response.text)
    return getXMLObjectVariable(data, "store.item", [], True)


def cleanHours(x):

    try:
        x = x.split(">")[1]
        x = x.split("<")[0]
        if len(x) < 3:
            return MISSING
        try:
            x = x.split("you;")[1]
        except Exception:
            x = x

        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
            .replace(";;", ";")
            .replace("Temporairement fermé;", "")
            .replace("Temporarily closed;", "")
        ).strip()

    except Exception:
        try:
            x = x.split("you;")[1]
        except Exception:
            x = x
        return (
            x.replace("day", "day:")
            .replace("::", ":")
            .replace("\n", "; ")
            .replace("\r", "; ")
            .replace(": ;", ": Closed;")
            .replace("&nbsp;", " ")
            .replace("Â", " ")
            .replace(";;", ";")
            .replace("Temporairement fermé;", "")
            .replace("Temporarily closed;", "")
        ).strip()


def getHOO(response):
    try:
        hours = html.fromstring(f"<div>{response.strip()}</div>", "lxml")
        hours = hours.xpath("//text()")
        hours = "; ".join(hours).replace("&nbsp;", " ")
    except Exception:
        return MISSING

    return cleanHours(hours)


def getAddress(raw_address):
    street_address = raw_address
    city = MISSING
    state = MISSING
    zip_postal = MISSING
    if "," in raw_address:
        parts = raw_address.split(", ")
        partsO = parts[0].strip()
        city = partsO.split(" ")[len(partsO.split(" ")) - 1]
        street_address = partsO.replace(f" {city}", "")

        parts1 = parts[1].strip()
        state = parts1.split(" ")[0]
        zip_postal = parts1.replace(f"{state} ", "")

    return raw_address, street_address, city, state, zip_postal


def fetchData():
    stores = fetchStores()
    log.info(f"Total stores = {len(stores)}")
    result = []
    for data in stores:
        locator_domain = website
        store_number = str(getXMLObjectVariable(data, "storeId")).strip()
        phone = getPhone(str(getXMLObjectVariable(data, "telephone"))).strip()
        latitude = str(getXMLObjectVariable(data, "latitude")).strip()
        longitude = str(getXMLObjectVariable(data, "longitude")).strip()
        page_url = MISSING
        location_name = str(getXMLObjectVariable(data, "location")).strip()
        raw_address = str(getXMLObjectVariable(data, "address")).strip()
        raw_address, street_address, city, state, zip_postal = getAddress(raw_address)

        country_code = str(getXMLObjectVariable(data, "country")).strip()

        hours_of_operation = getHOO(str(getXMLObjectVariable(data, "operatingHours")))

        location_type = MISSING
        if "Closed permanently" in hours_of_operation:
            location_type = "Closed permanently"
        if "Temporarily closed" in hours_of_operation:
            location_type = "Temporarily closed"

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

    return result


def scrape():
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total contact-us = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
