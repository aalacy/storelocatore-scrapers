import time
import re
from xml.etree import ElementTree as ET
from lxml import html

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgpostal import parse_address_intl

website = "https://thaiexpress.ca"
MISSING = "<MISSING>"

valid_day_parts = [
    "mon",
    "tues",
    "wednes",
    "thurs",
    "fri",
    "sat",
    "sun",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "to",
    "temporarily",
    "closed",
    "-",
]

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
    try:
        if Source is None or Source == "":
            return phone

        for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
            phone = match
            return phone.strip()
    except Exception as e:
        log.info(f"Phone:{phone} and err: {e}")
    return phone


def fetchStores():
    response = session.get(
        f"{website}/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php"
    )
    data = getXMLRoot(response.text)
    return getXMLObjectVariable(data, "store.item", [], True)


def isValidHooPart(part):
    for day_part in valid_day_parts:
        if part.lower().find(day_part) == -1:
            continue
        if "temporarily" == day_part:
            return ["Temporarily "]
        if "closed" == day_part:
            return ["closed"]
        if "to" == day_part:
            return ["to"]
        if "day" not in part:
            return [part]
        dayMatch = ""
        for match in re.findall(r"([a-zA-Z ]*/[a-zA-Z ]*)\d*.*", part):
            if len(match) > 0:
                dayMatch = match

        for match in re.findall(r"([a-zA-Z ]*)\d*.*", part):
            if len(match) > 0 and dayMatch == "":
                dayMatch = match
        if dayMatch == "":
            return [part]
        day = dayMatch
        for match in dayMatch.split("/"):
            if "day" in match:
                day = match + ": "
        return [day, part.replace(dayMatch, "")]
    return False


def getHOO(response):
    try:
        hours = html.fromstring(f"<div>{response.strip()}</div>", "lxml")
        hours = hours.xpath("//text()")
        hours = "; ".join(hours).replace("&nbsp;", " ")
    except Exception:
        return MISSING

    if hours == MISSING:
        return hours
    if "Closed permanently" in hours:
        return "Closed permanently"

    hours = hours.replace("\xa0", " ").replace("\n", " ").replace("&nbsp;", " ").strip()
    parts1 = re.split(r"[,; \!?:]+", hours)

    if len(parts1) == 0 or (len(parts1) == 1 and parts1[0] == ""):
        return MISSING
    parts = []
    for part in parts1:
        valid_parts = isValidHooPart(part)
        if valid_parts is not False:
            for valid_part in valid_parts:
                parts.append(valid_part)
    hoo = ""
    for part in parts:
        if hoo == "":
            if "Temporarily " == part or "day" in part.lower():
                hoo = part
            continue
        if part == "to":
            if (
                hoo.endswith("0")
                or hoo.endswith("1")
                or hoo.endswith("2")
                or hoo.endswith("3")
                or hoo.endswith("4")
                or hoo.endswith("5")
                or hoo.endswith("6")
                or hoo.endswith("7")
                or hoo.endswith("8")
                or hoo.endswith("9")
            ):
                hoo = hoo + " to "
            if hoo.endswith("day: "):
                hoo = hoo[:-2] + " to "
            continue
        if part.endswith(": "):
            if part in hoo:
                break
            if hoo.endswith(" to ") is False:
                hoo = hoo + "; "

        hoo = hoo + part
    return hoo


def getAddress(raw_address):
    try:
        data = parse_address_intl(raw_address)
        street_address = data.street_address_1
        if data.street_address_2 is not None:
            street_address = street_address + " " + data.street_address_2
        return street_address, data.city, data.state, data.postcode
    except Exception as e:
        log.info(f"Warning on address: {e}")
        return MISSING, MISSING, MISSING, MISSING


def getAddress2(raw_address):
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

    return street_address, city, state, zip_postal


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
        location_name = (
            str(getXMLObjectVariable(data, "location"))
            .replace("&#44;", ",")
            .replace(",,", ",")
            .strip()
        )
        raw_address = (
            str(getXMLObjectVariable(data, "address"))
            .replace("&#44;", ",")
            .replace(",,", ",")
            .replace("  ", " ")
            .strip()
        )
        street_address, city, state, zip_postal = getAddress(raw_address)

        # Known Issue:
        if raw_address == "5 Complexe Desjardins Montreal, QC H5B 1B8":
            street_address, city, state, zip_postal = getAddress2(raw_address)
        elif raw_address == "Space 821 - 66 Serramonte Center Daly City, CA 94015":
            street_address, city, state, zip_postal = getAddress2(raw_address)
        elif raw_address == "555 Saint-Charles-Borromee Joliette, QC J6E 4S5":
            street_address, city, state, zip_postal = getAddress2(raw_address)

        country_code = str(getXMLObjectVariable(data, "country")).strip()

        hours_of_operation = getHOO(str(getXMLObjectVariable(data, "operatingHours")))

        location_type = MISSING
        if "Closed permanently" in hours_of_operation:
            continue
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
    log.info("Removed: Closed permanently Store")
    log.info("Started")
    count = 0
    start = time.time()
    result = fetchData()
    with SgWriter() as writer:
        for rec in result:
            writer.write_row(rec)
            count = count + 1

    end = time.time()
    log.info(f"Total rows added = {count}")
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
