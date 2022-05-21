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


def get_additional(url):
    r = session.get(url, headers=headers)
    tree = html.fromstring(r.text)
    phone = "".join(
        tree.xpath("//div[@class='phone']//a[contains(@href, 'tel:')]/text()")
    ).strip()
    hoo = (
        "".join(tree.xpath("//div[@class='hours']//h2/text()"))
        .strip()
        .replace("\n", ";")
    )
    if "EVENT" in hoo:
        hoo = SgRecord.MISSING
    return phone, hoo


def fetch_data(sgw: SgWriter):
    api = "https://www.eatpdq.com/Widgets/LocationSearchResult.ashx"
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.content)
    markers = tree.xpath("//marker")

    for m in markers:
        location_name = "".join(m.xpath("./@name"))
        page_url = "".join(m.xpath("./@href"))
        if "coming" in page_url or "coming" in location_name.lower():
            continue
        raw_address = "".join(m.xpath("./@addresstext"))
        latitude = "".join(m.xpath("./@lat")).replace(",", ".")
        longitude = "".join(m.xpath("./@lng")).replace(",", ".")

        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        phone, hours_of_operation = get_additional(page_url)

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
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.eatpdq.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
