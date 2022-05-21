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


def fetch_data(sgw: SgWriter):
    page_url = "https://maritimeenergy.com/stores"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'et_pb_with_border et_pb_column_1_3 et_pb_column') and .//h2]"
    )

    for d in divs:
        location_name = "".join(d.xpath(".//h2/text()")).strip()
        store_number = "".join(d.xpath("./@id"))

        line = d.xpath(
            ".//a[contains(@href, 'goo.gl')]/preceding-sibling::text()|.//p[./a[contains(@href, 'goo.gl')]]/preceding-sibling::p//text()"
        )
        line = list(filter(None, [l.strip() for l in line]))
        if line[0][-1].isdigit():
            line.pop(0)

        raw_address = " ".join(line)
        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        try:
            pin = tree.xpath(
                f".//div[@class='et_pb_map_pin' and .//a[contains(@href, '{store_number}')]]"
            )[0]
            latitude = "".join(pin.xpath("./@data-lat"))
            longitude = "".join(pin.xpath("./@data-lng"))
        except:
            latitude = SgRecord.MISSING
            longitude = SgRecord.MISSING

        _tmp = []
        hours = d.xpath(
            ".//h3[contains(text(), 'Hours')]/following-sibling::p[1]/b|.//h3[contains(text(), 'Hours')]/following-sibling::p[1]/strong"
        )
        for h in hours:
            day = "".join(h.xpath("./text()")).strip()
            hour = "".join(h.xpath("./following-sibling::text()[1]")).strip()
            _tmp.append(f"{day} {hour}")

        hours_of_operation = ";".join(_tmp)
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
    locator_domain = "https://maritimeenergy.com/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
