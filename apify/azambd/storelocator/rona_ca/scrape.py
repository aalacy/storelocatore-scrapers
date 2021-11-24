from lxml import html
import time
import re
import json
from xml.etree import ElementTree as ET

from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord

DOMAIN = "rona.ca"
website = "https://www.rona.ca"
MISSING = "<MISSING>"


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}
session = SgRequests().requests_retry_session()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


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
    return session.get(url, headers=headers)


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
    JSObject = re.findall(f"{varName} = (.+?);", response)
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


def getHoo(body):
    lis = body.xpath("//div[@id='mainHours']/ul/li")
    hoo = []
    days = []
    for li in lis:
        day = getXpathClean(li, ".//span/text()")
        time = getXpathClean(li, ".//time/span/text()")
        if day in days:
            continue
        days.append(day)
        if time == MISSING:
            time = "Closed"
        hoo.append(day + " " + time)
    if len(hoo) == 0:
        return MISSING
    return "; ".join(hoo)


def fetchData():
    page_urls = fetchStores()
    log.info(f"Total stores = {len(page_urls)}")
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. fetching {page_url} ...")
        response = request_with_retries(page_url)
        body = html.fromstring(response.text, "lxml")
        storeDetails = getJSObject(response.text, "_storeDetails", {})
        storeDetails = storeDetails.replace("\u00E9", "").replace("\\'", "")
        storeDetails = json.loads(jsToPyDict(storeDetails))

        store_number = getJSONObjectVariable(storeDetails, "id")
        location_name = getJSONObjectVariable(storeDetails, "name")

        location_type = MISSING
        street_address = getXpathClean(body, "//span[@itemprop='streetAddress']/text()")
        city = getXpathClean(body, "//span[@itemprop='addressLocality']/text()")
        zip_postal = getXpathClean(body, "//span[@itemprop='postalCode']/text()")
        state = getXpathClean(body, "//span[@itemprop='addressRegion']/text()")
        country_code = "CA"
        phone = (
            getXpathClean(body, "//div[@itemprop='telephone']/text()")
            .replace("Phone:", "")
            .strip()
        )
        latitude = str(getJSObject(response.text, "lat"))
        longitude = str(getJSObject(response.text, "lng"))
        hours_of_operation = getHoo(body)
        raw_address = f"{street_address}, {city}, {state}, {zip_postal}"

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
