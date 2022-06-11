import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords(page_url):
    r = session.get(page_url)
    if r.status_code == 404:
        return SgRecord.MISSING, SgRecord.MISSING, False
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//iframe/@src"))
    try:
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()
    except IndexError:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
    iscoming = False
    if "Coming" in "".join(tree.xpath("//h1/text()")):
        iscoming = True

    return latitude, longitude, iscoming


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


def fetch_data(sgw: SgWriter):
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[@class='g-block  size-33-3' and .//div[@class='g-mosaicgrid-image']]"
    )
    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='g-mosaicgrid-item-title']//text()")
        ).strip()
        slug = location_name.split("-")[-1].strip().lower().replace(" ", "-")
        if "," in slug:
            slug = slug.split(",")[0]
        page_url = f"https://suncrestcare.com/location/{slug}"
        if "-" not in location_name:
            slug = "".join(d.xpath(".//div[@class='g-mosaicgrid-image']/a/@href"))
            page_url = f"https://suncrestcare.com{slug}"

        line = d.xpath(".//div[@class='g-mosaicgrid-item-desc']/text()")
        line = list(filter(None, [l.strip() for l in line]))
        if len(line) == 1:
            continue

        _tmp = []
        for li in line:
            _tmp.append(li)
            check = li.split()[-1]
            if len(check) == 5 and check.isdigit():
                break

        raw_address = ", ".join(_tmp)
        street_address, city, state, postal = get_address(raw_address)
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        latitude, longitude, iscoming = get_coords(page_url)
        hours_of_operation = SgRecord.MISSING
        if iscoming:
            hours_of_operation = "Coming Soon"

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


if __name__ == "__main__":
    locator_domain = "https://suncrestcare.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
