from lxml import html
from xml.etree import ElementTree as ET
import time
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

website = "staybridge.com"
MISSING = SgRecord.MISSING


session = SgRequests(verify_ssl=False)
log = sglog.SgLogSetup().get_logger(logger_name=website)


def get_XML_root(text):
    return ET.fromstring(text)


def XML_url_pull():
    response = get_response("https://www.ihg.com/bin/sitemapindex.xml")
    data = get_XML_root(
        response.text.replace('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', "")
    )
    links = []
    for url in get_XML_object_variable(data, "sitemap", [], True):
        link = get_XML_object_variable(url, "loc")

        if "staybridge.en.hoteldetail" not in link:
            continue
        log.info(f"link: {link}")
        response = get_response(link)
        data1 = get_XML_root(
            response.text.replace(
                'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"', ""
            )
        )
        for url1 in get_XML_object_variable(data1, "url", [], True):
            link2 = get_XML_object_variable(url1, "loc")
            links.append(link2)
    return links


def get_XML_object_variable(Object, varNames, noVal=MISSING, noText=False):
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


def get_response(url):
    return session.get(url)


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


def fetch_data():
    page_urls = XML_url_pull()
    log.info(f"Total stores = {len(page_urls)}")

    count = 0
    hours_of_operation = MISSING
    for page_url in page_urls:
        count = count + 1
        log.info(f"{count}. Scrapping {page_url} ...")
        store_number = page_url.split("/hoteldetail")[0].rsplit("/", 1)[1]
        location_type = "Hotel"
        response = get_response(page_url)
        log.info(f"Response: {response}")
        if response.status_code == 500:
            continue
        body = html.fromstring(response.text, "lxml")

        try:
            jsonData = body.xpath(
                '//script[contains(@type, "application/ld+json")]/text()'
            )[1]
            data = json.loads(jsonData)
            location_name = getJSONObjectVariable(data, "name")
        except Exception as e:
            log.error(f"{count} Error getting {page_url} ... {e}")
            continue

        location_type = getJSONObjectVariable(data, "@type")
        if len(location_type) == 0:
            location_type = MISSING

        street_address = getJSONObjectVariable(data, "address.streetAddress")
        city = getJSONObjectVariable(data, "address.addressLocality")
        zip_postal = getJSONObjectVariable(data, "address.postalCode")
        state = getJSONObjectVariable(data, "address.addressRegion")
        country_code = getJSONObjectVariable(data, "address.addressCountry")

        phone = getJSONObjectVariable(data, "telephone")
        latitude = str(getJSONObjectVariable(data, "geo.latitude"))
        longitude = str(getJSONObjectVariable(data, "geo.longitude"))

        raw_address = f"{street_address}, {city}, {state} {zip_postal}".replace(
            MISSING, ""
        )
        raw_address = " ".join(raw_address.split())
        raw_address = raw_address.replace(", ,", ",").replace(",,", ",")
        if raw_address[len(raw_address) - 1] == ",":
            raw_address = raw_address[:-1]

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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in fetch_data():
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
