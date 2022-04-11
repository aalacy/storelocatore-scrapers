import usaddress
from sglogging import sglog
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.uptowncheapskate.com/location-sitemap.xml", headers=headers
    )
    tree = html.fromstring(r.content)

    return tree.xpath("//loc/text()")


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
    adr1 = a.get("address1") or ""
    adr2 = a.get("address2") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_data(page_url, sgw: SgWriter):
    try:
        r = session.get(page_url, headers=headers)
        tree = html.fromstring(r.text)
    except Exception as e:
        logger.info(f"{page_url}: {e}")
        return

    location_name = " - ".join(tree.xpath("//h1/text()")).strip()
    _tmp = []
    line = tree.xpath("//a[@class='storeAddress']/p/text()")
    line = list(filter(None, [li.strip() for li in line]))
    for li in line:
        if "Text" in li:
            continue
        _tmp.append(li)
    raw_address = " ".join(_tmp)
    if not raw_address:
        logger.info(f"{page_url}: COMING SOON")
        return
    street_address, city, state, postal = get_address(raw_address)
    country_code = "US"
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]//text()")).strip()

    hours = tree.xpath(
        "//div[./div/h2[contains(text(), 'Store Hours')]]/following-sibling::div//text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = ";".join(hours)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.uptowncheapskate.com/"
    logger = sglog.SgLogSetup().get_logger(logger_name="uptowncheapskate.com")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
