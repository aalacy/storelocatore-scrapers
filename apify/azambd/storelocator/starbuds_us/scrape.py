import json
import time
from lxml import html

from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

MISSING = SgRecord.MISSING
DOMAIN = "starbuds.us"
website = "https://www.starbuds.us"
session = SgRequests()
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)


def fetch_node_text(node):
    results = []
    for i, text_line in enumerate(node):
        span_text = [x.strip() for x in text_line.xpath(".//text()")]
        results.append(span_text)
    return results


def get_feature_data(url):
    response = session.get(url)
    body = html.fromstring(response.text, "lxml")
    featuredJsonLink = body.xpath(
        '//link[contains(@id, "features_") and @id != "features_masterPage"]/@href'
    )[0]

    response = session.get(featuredJsonLink)
    return {"data": json.loads(response.text), "body": body}


def fetch_location_stores(url):
    compProps = get_feature_data(url)["data"]["props"]["render"]["compProps"]
    storeLinks = []
    for key in compProps.keys():
        if (
            "label" in compProps[key]
            and compProps[key]["label"] == "VIEW HOURS, SPECIALS AND MENU"
        ):
            storeLinks.append(compProps[key]["link"]["href"])
    return storeLinks


def fetch_store_links():
    compProps = get_feature_data(website + "/locations")["data"]["props"]["render"][
        "compProps"
    ]
    storeLinks = []
    for key in compProps.keys():
        if "skin" in compProps[key] and compProps[key]["skin"] == "BasicButton":
            url = compProps[key]["link"]["href"]
            if "LOCATIONS" in compProps[key]["label"]:
                for link in fetch_location_stores(url):
                    if link not in storeLinks:
                        storeLinks.append(link)
            elif url not in storeLinks:
                storeLinks.append(url)
    storeLinks.sort()
    return storeLinks


def fetch_store_details(link):
    featuredData = get_feature_data(link)
    body = featuredData["body"]
    data = featuredData["data"]

    location_name = (
        (" ".join(body.xpath("//h1/span/span/text()")))
        .replace("Coming Soon!", "")
        .replace("&nbsp;", " ")
        .strip()
    )

    phone = body.xpath('//a[contains(@href, "tel:")]/span/span/text()')
    if len(phone) == 0:
        phone = body.xpath('//a[contains(@href, "tel:")]/span/text()')
        if len(phone) == 0:
            phone = body.xpath(
                '//span[contains(text(), "(") and contains(text(), ")")]/text()'
            )
            if len(phone) == 0:
                phone = [MISSING]

    phone = phone[0].replace("tel:", "").strip()

    operations = []
    hoursP = body.xpath("//span[text()='HOURS']")
    for hourP in hoursP:
        parentDiv = hourP.getparent().getparent().getparent().getparent()
        dayParts = fetch_node_text(parentDiv)
        for dayPart in dayParts[1:]:
            operations.append("".join(dayPart))

    location_type = MISSING
    if len(operations) == 0:
        phone = MISSING
    if phone == MISSING:
        location_type = "coming soon"
    location = {}
    foundLocation = False
    compProps = data["props"]["render"]["compProps"]
    for key in compProps.keys():
        if "mapData" in compProps[key]:
            location = compProps[key]["mapData"]["locations"][0]
            foundLocation = True
    store_number = data["props"]["seo"]["pageId"]

    if foundLocation == False:

        for script in body.xpath('.//script[@type="application/ld+json" ]/text()'):
            if "latitude" in script:
                script = script.replace("\n", " ")
                data1 = json.loads(script)
                geo = data1["geo"]
                address = data1["address"]
                address = f"{address['streetAddress']} {address['addressLocality']}, {address['addressRegion']} {address['postalCode']}, USA".replace(
                    "Colorado", "CO"
                )

                location = {
                    "latitude": geo["latitude"],
                    "longitude": geo["longitude"],
                    "address": address,
                }

    return {
        "location_name": location_name,
        "phone": phone,
        "operations": ", ".join(operations),
        "location": location,
        "store_number": store_number,
        "location_type": location_type,
    }


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
            return street_address, city, state, zip_postal
    except Exception as e:
        log.info(f"Invalid Address : {e}")
        pass
    return MISSING, MISSING, MISSING, MISSING


def fetch_data():
    page_urls = fetch_store_links()
    log.debug(f"Total store count={len(page_urls)}")
    count = 0
    for page_url in page_urls:
        count = count + 1
        log.debug(f"{count}. scrapping {page_url}")
        details = fetch_store_details(page_url)

        country_code = "US"
        location_name = details["location_name"]
        phone = details["phone"]
        operations = details["operations"]
        store_number = details["store_number"]
        location_type = details["location_type"]
        location = details["location"]

        raw_address = location["address"]
        latitude = str(location["latitude"])
        longitude = str(location["longitude"])

        street_address, city, state, zip_postal = get_address(raw_address)
        if state == MISSING and ", CO ":  # special case for only 1 row
            state = "CO"

        if "USA" not in raw_address:
            continue

        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=zip_postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=operations,
            location_type=location_type,
            raw_address=raw_address,
        )


def scrape():
    log.info(f"Start Crawling {website} ...")
    start = time.time()
    result = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in result:
            writer.write_row(rec)
    end = time.time()
    log.info(f"Scrape took {end-start} seconds.")


if __name__ == "__main__":
    scrape()
