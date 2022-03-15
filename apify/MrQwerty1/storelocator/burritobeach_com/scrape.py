import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1K5owjFYA9Cmw-5LeqANVtvPEqzM&forcekml=1",
        headers=headers,
    )
    source = r.text.replace("<![CDATA[", "").replace("]]>", "")
    tree = html.fromstring(source.encode())
    markers = tree.xpath("//placemark")
    for m in markers:
        key = (
            "".join(m.xpath("./name/text()")).split("–")[-1].strip().split()[0].lower()
        )
        value = "".join(m.xpath(".//coordinates/text()")).replace(",0", "").split(",")
        coords[key] = value

    return coords


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
        street_address = SgRecord.MISSING
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "https://burritobeach.com/locations"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[@class='location-div' and not(.//a[contains(@href, 'mailto')])]"
    )
    coords = get_coords()

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        slug = location_name.lower()
        if "st." in slug:
            slug = "streeterville"

        for k, v in coords.items():
            if k in slug:
                latitude = v[1].strip()
                longitude = v[0].strip()

        line = "".join(
            d.xpath(".//p[./span[@class='fa fa-map-marker']][1]/text()")
        ).strip()
        street_address, city, state, postal = get_address(line)
        phone = (
            "".join(d.xpath(".//p[./span[@class='fa fa-phone']]/text()"))
            .replace("P:", "")
            .strip()
        )

        hours = d.xpath(".//p[./span[@class='fa fa-clock-o']]/text()")
        hours = list(
            filter(
                None,
                [h.replace("amâ", " - ").replace("Hours", "").strip() for h in hours],
            )
        )
        hours_of_operation = ";".join(hours)
        if "closed" in hours_of_operation:
            hours_of_operation = "Closed"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://burritobeach.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests(verify_ssl=False)
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
