import re
from lxml import html
from xml.etree import ElementTree as ET
import time
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

website = "hotelindigo.com"
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

        if "hotelindigo.en.hoteldetail" not in link:
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


def get_empty_string(string=""):
    if string is None or string == MISSING:
        return MISSING
    string = f"{string}".replace(".0", "").replace("-|", "").replace("|", "").strip()

    if string == "" or string == "nan" or "-- ---" in string:
        return MISSING
    return string


def stringify_nodes(body, xpath):
    nodes = body.xpath(xpath)
    values = []
    for node in nodes:
        for text in node.itertext():
            text = text.strip()
            if text:
                values.append(text)
    if len(values) == 0:
        return MISSING
    return get_empty_string(" ".join((" ".join(values)).split()))


def get_phone(Source):
    phone = MISSING

    if Source is None or Source == "":
        return phone

    for match in re.findall(r"[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]", Source):
        phone = match
        return phone
    return phone


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
        body = html.fromstring(response.text, "lxml")

        location_name = stringify_nodes(body, "//h1/span")
        if location_name == MISSING:
            log.error(f"{count}. {page_url} not found")
            continue
        street_address = stringify_nodes(body, '//span[@itemprop="streetAddress"]')
        city = stringify_nodes(body, '//span[@itemprop="addressLocality"]')
        zip_postal = stringify_nodes(body, '//span[@itemprop="postalCode"]')
        state = stringify_nodes(body, '//span[@itemprop="addressRegion"]')
        country_code = stringify_nodes(body, '//span[@itemprop="addressCountry"]')
        phone = get_phone(
            stringify_nodes(body, '//span[@itemprop="telephone"]')
        ).split()[0]
        latitude = body.xpath('//meta[@itemprop="latitude"]/@content')
        longitude = body.xpath('//meta[@itemprop="longitude"]/@content')

        if len(latitude) == 0:
            latitude = MISSING
        else:
            latitude = latitude[0]

        if len(longitude) == 0:
            longitude = MISSING
        else:
            longitude = longitude[0]

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
