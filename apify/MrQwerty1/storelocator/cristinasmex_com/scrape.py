import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


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


def get_coords():
    coords = dict()
    r = session.get(
        "https://www.google.com/maps/d/u/0/kml?mid=1ZVKhKWXpiBwOxwJ_vtP9zwB7q5l6--PA&forcekml=1"
    )
    source = r.text.replace("<![CDATA[", "").replace("]]>", "")
    tree = html.fromstring(source.encode("utf8"))
    markers = tree.xpath("//placemark")
    for marker in markers:
        name = "".join(marker.xpath(".//name/text()")).strip()
        key = name.split("-")[-1].strip().lower()
        lng, lat = "".join(marker.xpath(".//coordinates/text()")).split(",")[:2]
        lng, lat = lng.strip(), lat.strip()
        coords[key] = (lat, lng)

    return coords


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='col-12 col-md-4 col-sm-6']")
    coords = get_coords()

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        raw_address = " ".join(
            " ".join(d.xpath(".//a[contains(@href, 'maps')]/text()")).split()
        )
        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        phone = "".join(d.xpath(".//a[@class='location-phone']/text()")).strip()
        key = location_name.lower()
        latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)

        hours = d.xpath(
            ".//strong[contains(text(), 'Hours')]/following-sibling::text()"
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
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://cristinasmex.com/"
    page_url = "https://cristinasmex.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
