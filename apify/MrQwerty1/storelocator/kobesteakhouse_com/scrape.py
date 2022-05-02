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

    raw_address = " ".join(
        "".join(tree.xpath("//p[@class='location__address']/text()")).split()
    )
    street, city, state, post = get_address(raw_address)

    hours = tree.xpath("//strong[contains(text(), 'Dining')]/following-sibling::text()")
    hours = list(filter(None, [h.strip() for h in hours]))
    hoo = ";".join(hours)

    if tree.xpath("//p[contains(text(), 'temporarily closed')]"):
        hoo = "Temporarily Closed"

    return {
        "street": street,
        "city": city,
        "state": state,
        "postal": post,
        "hoo": hoo,
        "raw": raw_address,
    }


def fetch_data(sgw: SgWriter):
    api = "https://kobesteakhouse.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUFni6FAPFomOBAsmlxSX5uW6ZqTkpELFapVoABU0Wug"
    r = session.get(api, headers=headers)
    js = r.json()["markers"]

    for j in js:
        page_url = j.get("link")
        a = get_additional(page_url) or {}
        raw_address = a.get("raw")
        street_address = a.get("street")
        city = a.get("city")
        state = a.get("state")
        postal = a.get("postal")
        country_code = "US"
        source = j.get("description") or ""
        tree = html.fromstring(source)
        location_name = j.get("title")
        phone = "".join(tree.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        latitude = j.get("lat")
        longitude = j.get("lng")
        hours_of_operation = a.get("hoo")

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
    locator_domain = "https://kobesteakhouse.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
