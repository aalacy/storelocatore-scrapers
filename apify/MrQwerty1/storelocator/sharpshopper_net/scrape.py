import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


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


def get_urls():
    r = session.get(locator_domain)
    tree = html.fromstring(r.text)

    return tree.xpath("//a[text()='Locations']/following-sibling::ul[1]//a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"{locator_domain}{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).strip()
    line = tree.xpath("//h1/text()")
    line = list(filter(None, [l.strip() for l in line]))
    raw_address = ", ".join(line[1:])

    street_address, city, state, postal = get_address(raw_address)
    phone = "".join(
        tree.xpath("//div[@class='contentright']/h3/following-sibling::p[1]/text()")
    ).strip()
    if "Phone" in phone:
        phone = phone.split("Phone")[1].replace("#", "").replace(":", "").strip()
    if "Fax" in phone:
        phone = phone.split("Fax")[0].strip()
    location_type = location_name.split()[-1]

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), ' Hours')]/following-sibling::p[1]/strong"
    )
    for h in hours:
        day = "".join(h.xpath("./text()")).strip()
        inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
        if "sunday" in day.lower() and "closed" in inter.lower():
            _tmp.append(f"{day} Closed")
            break
        if "@" in inter:
            break
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
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "http://sharpshopper.net/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
