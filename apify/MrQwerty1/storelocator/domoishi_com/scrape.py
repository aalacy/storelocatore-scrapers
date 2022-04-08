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
    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1PnrcKVsqqg1j7M1anxqXntvC97g_66if&forcekml=1"
    )
    tree = html.fromstring(r.content)
    markers = tree.xpath("//placemark")
    for marker in markers:
        name = "".join(marker.xpath("./name/text()")).strip()
        key = name.lower().replace("domoishi", "").replace("domoish", "").strip()
        coords[key] = "".join(marker.xpath(".//coordinates/text()")).strip()

    return coords


def get_urls():
    r = session.get("https://domoishi.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='elementor-image']/a/@href")


def fetch_data(sgw: SgWriter):
    urls = get_urls()
    coords = get_coords()

    for page_url in urls:
        r = session.get(page_url)
        tree = html.fromstring(r.text)
        divs = tree.xpath(
            "//div[contains(@class, 'elementor-column elementor-col-50') and .//h2]"
        )

        for d in divs:
            location_name = "".join(d.xpath(".//h2/text()")).strip()
            line = d.xpath(
                ".//div[contains(@class, 'elementor-widget elementor-widget-text-editor')]//text()"
            )
            line = list(filter(None, [l.strip() for l in line]))
            iscoming = d.xpath(".//span[contains(text(), 'Coming Soon')]")
            if iscoming or not line:
                continue

            phone = line.pop().replace("Phone:", "").strip()
            raw_address = ", ".join(line)
            street_address, city, state, postal = get_address(raw_address)
            try:
                longitude, latitude = coords[location_name.lower()].split(",")[:2]
            except:
                longitude, latitude = SgRecord.MISSING, SgRecord.MISSING

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
                raw_address=raw_address,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://domoishi.com/"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
