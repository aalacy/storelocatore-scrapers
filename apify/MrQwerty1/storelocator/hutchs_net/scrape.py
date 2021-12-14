import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


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


def get_raw(page_url):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    raw = "".join(tree.xpath("//title/text()")).split("|")[0].strip()

    return raw


def fetch_data(sgw: SgWriter):
    api = "https://www.hutchs.net/locations/"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-wrapper']")

    for d in divs:
        page_url = "".join(d.xpath(".//a[@class='location-link']/@href"))
        raw_address = " ".join(
            d.xpath(".//a[@class='location-link']/following-sibling::h5[1]/text()")
        ).strip()
        if raw_address == ",":
            raw_address = get_raw(page_url)
        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        location_name = "".join(d.xpath(".//a[@class='location-link']//text()")).strip()
        store_number = location_name.split()[-1]
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/h5/text()")).strip()

        try:
            pin = tree.xpath(
                f"//div[@class='marker' and .//a[contains(@href, '{page_url}')]]"
            )[0]
            latitude = "".join(pin.xpath("./@data-lat"))
            longitude = "".join(pin.xpath("./@data-lng"))
        except:
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING
        hours_of_operation = (
            "".join(
                d.xpath(
                    ".//div[@class='location-amenities']/preceding-sibling::h5[1]/text()"
                )
            )
            .strip()
            .replace("\r\n", ";")
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.hutchs.net/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
