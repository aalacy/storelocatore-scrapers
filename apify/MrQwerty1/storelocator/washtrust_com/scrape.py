import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


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
    if not street_address:
        street_address = line.split(",")[0].strip()
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_hours(page_url):
    li = []
    _tmp = []
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    ul = tree.xpath("//div[@class='full-content']/ul")

    for u in ul:
        text = "".join(u.xpath("./preceding-sibling::*[1]//text()"))
        if "lobby" in text.lower():
            li = u.xpath("./li")
            break

    for l in li:
        text = " ".join("".join(l.xpath(".//text()")).split())
        if ":" in text:
            _tmp.append(text)

    if not _tmp:
        lines = tree.xpath(
            "//div[@class='full-content']/p[./strong[contains(text(), 'Lobby')]]/text()"
        )
        lines = list(filter(None, [l.strip() for l in lines]))
        _tmp = lines

    if not _tmp:
        _tmp = tree.xpath(
            "//div[@class='full-content']/p[./strong[contains(text(), 'Lobby')]]/following-sibling::*[1]//text()"
        )

    if not _tmp:
        text = tree.xpath("//div[@class='full-content']/p/text()")
        for t in text:
            if "Monday" in t:
                _tmp.append(t.strip())

    return ";".join(_tmp)


def fetch_data(sgw: SgWriter):
    api = "https://www.washtrust.com/about/locations"
    r = session.get(api)
    tree = html.fromstring(r.text)
    li = tree.xpath("//div[@class='location-results']/ul/li")
    coords = dict()

    text = "".join(tree.xpath("//div[@data-dna]/@data-dna"))
    js = json.loads(text)[1:]
    for j in js:
        try:
            lat = j["locations"][0]["lat"]
            lng = j["locations"][0]["lng"]
        except:
            continue
        source = j["options"]["infoWindowOptions"]["content"]
        root = html.fromstring(source)
        name = "".join(root.xpath("./h3/text()")).strip()
        coords[name] = (lat, lng)

    for l in li:
        location_name = "".join(l.xpath("./strong/text()|./a/text()")).strip()
        raw_address = "".join(l.xpath("./span[@class='address']/text()")).strip()
        street_address, city, state, postal = get_address(raw_address)

        page_url = "".join(l.xpath(".//a[@class='arrow-link']/@href")) or api
        phone = "".join(l.xpath("./span[@class='phone']/text()")).strip()
        latitude, longitude = coords.get(location_name) or ["<MISSING>", "<MISSING>"]
        if "ATM" in location_name:
            location_type = "ATM"
        else:
            location_type = "Branch"

        if page_url != api:
            hours_of_operation = get_hours(page_url)
        else:
            hours_of_operation = SgRecord.MISSING
        if "Opening" in location_name:
            hours_of_operation = "Coming Soon"

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
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.washtrust.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.RAW_ADDRESS, SgRecord.Headers.LOCATION_NAME})
        )
    ) as writer:
        fetch_data(writer)
