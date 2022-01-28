import time
import re
import json
from xml.etree import ElementTree as ET

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from tenacity import retry, stop_after_attempt
import tenacity
import random

DOMAIN = "rona.ca"
website = "https://www.rona.ca"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

# Testing:stop using tenacity


@retry(stop=stop_after_attempt(3), wait=tenacity.wait_fixed(5))
def get_response(idx, url):
    with SgRequests() as http:
        response = http.get(url, headers=headers)
        log.info(response)
        time.sleep(random.randint(1, 3))
        if response.status_code == 200:
            log.info(f"[{idx}] | {url} >> HTTP STATUS: {response.status_code}")
            return response


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


def request_with_retries(url):
    r = session.get(url, headers=headers)
    log.info(r)
    return r


def fetchStores():
    response = request_with_retries(f"{website}/sitemap-stores-en.xml")
    data = getXMLRoot(
        response.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', "")
    )
    links = []
    for url in getXMLObjectVariable(data, "url", [], True):
        links.append(getXMLObjectVariable(url, "loc"))
    return links


def getJSObject(response, varName, noVal=MISSING):
    JSObject = re.findall(f"{varName} = (.+?)<", response)
    if JSObject is None or len(JSObject) == 0:
        return noVal
    return JSObject[0]


def jsToPyDict(value):
    quote_keys_regex = r"([\{\s,])(\w+)(:)"
    return re.sub(quote_keys_regex, r'\1"\2"\3', value)


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


def getXpathClean(body, xpath):
    values = body.xpath(xpath)
    if len(values) == 0:
        return MISSING
    return values[0].strip()


def fetchData():
    error_urls = []
    page_urls = fetchStores()
    log.info(f"Total stores = {len(page_urls)}")
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. fetching {page_url} ...")
        response = get_response(count, page_url)
        if response is None:
            error_urls.append(page_url)
            continue

        storeDetails = getJSObject(response.text, "]", {})
        storeDetails = storeDetails.replace("\u00E9", "").replace("\\'", "")

        storeDetails = json.loads(storeDetails)

        store_number = getJSONObjectVariable(storeDetails, "storeDetails.id")
        location_name = getJSONObjectVariable(storeDetails, "storeDetails.store_name")
        latitude = str(getJSONObjectVariable(storeDetails, "storeDetails.lat"))
        longitude = str(getJSONObjectVariable(storeDetails, "storeDetails.long"))
        phone = str(getJSONObjectVariable(storeDetails, "storeDetails.phone"))
        city = getJSONObjectVariable(storeDetails, "storeDetails.city")
        zip_postal = getJSONObjectVariable(storeDetails, "storeDetails.zip")
        state = getJSONObjectVariable(storeDetails, "storeDetails.state")
        street_address = getJSONObjectVariable(storeDetails, "storeDetails.address")
        country_code = getJSONObjectVariable(storeDetails, "storeDetails.country")

        location_type = MISSING

        info_hoo = storeDetails["storeDetails"]["storeHours"]
        hoos = []
        for t in info_hoo:
            hoo = f"{t['day']['day']}:{t['day']['open']}-{t['day']['close']}"
            hoos.append(hoo)

        hours_of_operation = "; ".join(hoos)

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
        )

    log.info(f"All Bad 500 urls: {error_urls}")


def scrape():
    log.info(f"Start crawling {website} ...")
    start = time.time()
    result = fetchData()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
