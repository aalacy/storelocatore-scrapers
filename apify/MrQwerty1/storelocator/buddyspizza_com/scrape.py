from urllib.parse import unquote
import usaddress
from lxml import html
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgwriter import SgWriter


logger = SgLogSetup().get_logger("buddyspizza_com")


DOMAIN = "https://www.buddyspizza.com"
URL_LOCATION = "https://www.buddyspizza.com/locations"
MISSING = "<MISSING>"

headers_custom_for_location_url = {
    "authority": "www.buddyspizza.com",
    "method": "GET",
    "path": "/locations",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "upgrade-insecure-requests": "1",
}

session = SgRequests()


def get_address(line):
    tag = {
        "Recipient": "recipient",
        "AddressNumber": "address1",
        "AddressNumberPrefix": "address1",
        "AddressNumberSuffix": "address1",
        "StreetName": "address1",
        "StreetNamePreDirectional": "address1",
        "StreetNamePreModifier": "address1",
        "StreetNamePreType": "address1",
        "StreetNamePostDirectional": "address1",
        "StreetNamePostModifier": "address1",
        "StreetNamePostType": "address1",
        "CornerOf": "address1",
        "IntersectionSeparator": "address1",
        "LandmarkName": "address1",
        "USPSBoxGroupID": "address1",
        "USPSBoxGroupType": "address1",
        "USPSBoxID": "address1",
        "USPSBoxType": "address1",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }

    a = usaddress.tag(line, tag_mapping=tag)[0]
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
    if street_address == "None":
        street_address = MISSING
    city = a.get("city") or MISSING
    state = a.get("state") or MISSING
    postal = a.get("postal") or MISSING

    return street_address, city, state, postal


def get_coords_from_embed(text):
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        try:
            longitude = text.split("!2d")[1].strip().split("!")[0].strip()
        except IndexError:
            longitude = text.split("!4d")[1].strip().split("?")[0].strip()
    except IndexError:
        latitude, longitude = MISSING, MISSING

    return latitude, longitude


def get_urls():

    r = session.get(URL_LOCATION, headers=headers_custom_for_location_url)
    tree = html.fromstring(r.text, "lxml")
    return tree.xpath("//div[@class='image-slide-title']/preceding-sibling::a/@href")


def fetch_data():
    urls = get_urls()
    for page_num, url in enumerate(urls):
        locator_domain = DOMAIN
        page_url = f"https://www.buddyspizza.com{url}"
        logger.info(f"Pulling the data from Page Num: {page_num} --> {page_url} ")
        headers_custom_with_url_path = {
            "authority": "www.buddyspizza.com",
            "method": "GET",
            "path": url,
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "referer": "https://www.buddyspizza.com/locations",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
            "upgrade-insecure-requests": "1",
        }

        r = session.get(page_url, headers=headers_custom_with_url_path)
        tree = html.fromstring(r.text, "lxml")
        location_name = tree.xpath("//meta[@itemprop='name']/@content")
        location_name = [" ".join(ln.split()) for ln in location_name]
        location_name = "".join(location_name) if location_name else MISSING

        # Parse Address using usaddress
        line = tree.xpath("//p[./strong[contains(text(), 'Address')]]/text()")
        logger.info(f"Raw Addresses: {line}")
        line = [" ".join(i.split()) for i in line]
        line = ", ".join(list(filter(None, [l.strip() for l in line])))

        street_address, city, state, postal = get_address(line)
        country_code = "US"
        store_number = MISSING

        # Phone
        phone = (
            "".join(
                tree.xpath("//p[./strong[contains(text(), 'Phone')]]/a/text()")
            ).strip()
            or MISSING
        )

        # Latitude and Longitude
        text = unquote(
            "".join(
                tree.xpath(
                    "//div[contains(@data-block-json, 'iframe')]/@data-block-json"
                )
            )
        )
        latitude, longitude = get_coords_from_embed(text)
        location_type = MISSING

        # Hours of Operation
        hours = tree.xpath(
            "//h3[text()='Hours']/following-sibling::p/text()|//h3[./strong[contains(text(), 'Hours')]]/following-sibling::p/text()"
        )
        logger.info(f"Raw hours data: {hours}")

        hours = list(filter(None, [h.strip() for h in hours]))
        hours = [" ".join(i.split()) for i in hours]
        if len(hours) > 7:
            hours = hours[:7]
        hours_of_operation = "; ".join(hours).replace("*", "") or MISSING
        if ";Dine-in" in hours_of_operation:
            hours_of_operation = hours_of_operation.split(";Dine-in")[0]
        if tree.xpath("//h3[contains(text(), 'Coming Soon')]"):
            hours_of_operation = "Coming Soon"

        raw_address = line
        yield SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    logger.info("Started")
    count = 0
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    logger.info(f"No of records being processed: {count}")
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
