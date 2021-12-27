import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()

    r = session.get(
        "https://www.selfmadetrainingfacility.com/locations", headers=headers
    )
    tree = html.fromstring(r.text)
    states = tree.xpath(
        "//div[contains(@class, 'brz-row__container')]/preceding-sibling::div[1]//a[@class='brz-a']/@href"
    )
    for state in states:
        url = f"https://www.selfmadetrainingfacility.com{state}"
        req = session.get(url, headers=headers)
        root = html.fromstring(req.text)
        links = root.xpath(
            "//div[contains(@class, 'brz-columns') and .//picture]//a[contains(@class, 'brz-a')]/@href"
        )
        for link in links:
            link = link.strip()
            if link == "/home" or link.find(".com") != -1:
                continue
            urls.add(f"https://www.selfmadetrainingfacility.com{link}")

    return urls


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
        "BuildingName": "address2",
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
        street_address = SgRecord.MISSING
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(
        tree.xpath(
            "//span[@class='brz-cp-color8' and contains(text(), 'Self Made')]/text()"
        )
    ).strip()
    raw_address = "".join(
        tree.xpath(
            "//h4[./span[contains(text(), 'Address')]]/following-sibling::p//text()"
        )
    ).strip()
    if "Soon" in raw_address:
        return
    street_address, city, state, postal = get_address(raw_address)
    phone = "".join(
        tree.xpath(
            "//h4[./span[contains(text(), 'Phone')]]/following-sibling::p//text()"
        )
    ).strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.selfmadetrainingfacility.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
