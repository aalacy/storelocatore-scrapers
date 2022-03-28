import json
import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def write(data, sgw):
    row = SgRecord(
        page_url=data.get("page_url"),
        location_name=data.get("location_name"),
        street_address=data.get("street_address"),
        city=data.get("city"),
        state=data.get("state"),
        zip_postal=data.get("postal"),
        country_code="US",
        phone=data.get("phone"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        locator_domain=locator_domain,
        hours_of_operation=data.get("hours_of_operation"),
        raw_address=data.get("raw_address"),
    )

    sgw.write_row(row)


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


def get_states():
    r = session.get("https://www.mrniceguyretail.com/locations-main-page")
    tree = html.fromstring(r.text)

    return tree.xpath("//div[@class='col sqs-col-6 span-6' and .//a]//a/@href")


def get_default(slug, sgw):
    page_url = f"https://www.mrniceguyretail.com{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//h1//text()")).strip()
    raw_address = (
        "".join(
            tree.xpath(
                "//p[.//*[contains(text(), 'Address')]]/text()|//p[contains(text(), 'Address')]/text()"
            )
        )
        .replace("Address:", "")
        .strip()
    )
    street_address, city, state, postal = get_address(raw_address)
    city = city.replace("in ", "")
    phone = (
        "".join(
            tree.xpath(
                "//p[.//*[contains(text(), 'Phone')]]/text()|//p[contains(text(), 'Phone')]/text()"
            )
        )
        .replace("Phone:", "")
        .strip()
    )
    hours_of_operation = (
        "".join(
            tree.xpath(
                "//p[.//*[contains(text(), 'Hours')]]/text()|//p[contains(text(), 'Hours')]/text()"
            )
        )
        .replace("Hours:", "")
        .strip()
    )

    block = "".join(
        tree.xpath("//div[contains(@data-block-json, 'location')]/@data-block-json")
    )
    if block:
        j = json.loads(block)["location"]
        latitude = j.get("markerLat")
        longitude = j.get("markerLng")
    else:
        text = "".join(tree.xpath("//iframe/@src"))
        latitude = text.split("!3d")[1].strip().split("!")[0].strip()
        longitude = text.split("!2d")[1].strip().split("!")[0].strip()

    data = {
        "location_name": location_name,
        "page_url": page_url,
        "street_address": street_address,
        "city": city,
        "state": state,
        "postal": postal,
        "phone": phone,
        "latitude": latitude,
        "longitude": longitude,
        "hours_of_operation": hours_of_operation,
        "raw_address": raw_address,
    }

    write(data, sgw)


def fetch_data(sgw: SgWriter):
    states = get_states()
    for state_slug in states:
        api = f"https://www.mrniceguyretail.com{state_slug}"
        r = session.get(api)
        tree = html.fromstring(r.text)

        divs = tree.xpath(
            "//div[@class='row sqs-row' and .//noscript]/div[not(.//a[contains(text(), 'ORDER')])]"
        )
        for d in divs:
            if not d.xpath(".//noscript") or d.xpath(
                './/img[contains(@alt, "Coming")]'
            ):
                continue

            slug = "".join(d.xpath(".//a[@class='sqs-button-element--primary']/@href"))
            if slug:
                get_default(slug, sgw)
                continue

            line = d.xpath(".//text()")
            line = list(filter(None, [l.replace("Now Open", "").strip() for l in line]))
            location_name = line.pop(0)
            phone = line.pop()
            raw_address = line.pop()
            raw = raw_address.split(", ")
            street_address = raw.pop(0)
            city = raw.pop(0)
            state, postal = raw.pop(0).split()
            text = "".join(d.xpath(".//a/@href"))
            latitude, longitude = text.split("/@")[1].split(",")[:2]

            data = {
                "location_name": location_name,
                "page_url": api,
                "street_address": street_address,
                "city": city,
                "state": state,
                "postal": postal,
                "phone": phone,
                "latitude": latitude,
                "longitude": longitude,
                "raw_address": raw_address,
            }
            write(data, sgw)


if __name__ == "__main__":
    locator_domain = "https://www.mrniceguyretail.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
