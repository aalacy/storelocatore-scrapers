import re
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    coords = dict()
    r = session.get("https://acfp.com/locations")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'latitude')]/text()")).split(
        "coords:"
    )
    text.pop(0)
    for t in text:
        lat = t.split('"')[1]
        lng = t.split('"')[3]
        key = (
            t.split("tel:")[1]
            .split('"')[1]
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
        )
        coords[key] = (lat, lng)

    urls = set(
        re.findall(
            r'https:\\u002F\\u002Fwp.acfp.com\\u002Flocations\\u002F[^"]+?\\u002F',
            r.text,
        )
    )

    return urls, coords


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


def get_data(page_url, coords, sgw: SgWriter):
    page_url = page_url.replace("wp.", "").replace("\\u002F", "/")
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    if not location_name:
        location_name = "".join(tree.xpath("//title/text()")).split("-")[0].strip()
    raw_address = "".join(
        tree.xpath("//div[@class='info-field address']/div//text()")
    ).strip()
    street_address, city, state, postal = get_address(raw_address)
    phone = "".join(tree.xpath("//a[contains(@href, 'tel:')]/text()")).strip()
    key = phone.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    latitude, longitude = coords.get(key)

    _tmp = []
    hours = tree.xpath("//div[@class='times']/div")
    for h in hours:
        day = "".join(h.xpath("./p[1]//text()")).strip()
        inter = "".join(h.xpath("./p[2]//text()")).strip()
        _tmp.append(f"{day} {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls, coords = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, url, coords, sgw): url for url in urls
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://acfp.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
