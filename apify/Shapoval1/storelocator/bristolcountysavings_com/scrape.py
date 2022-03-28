import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://bristolcountysavings.com"
    api_url = "https://bristolcountysavings.com/locations"
    session = SgRequests()
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
        "BuildingName": "address2",
        "OccupancyType": "address2",
        "OccupancyIdentifier": "address2",
        "SubaddressIdentifier": "address2",
        "SubaddressType": "address2",
        "PlaceName": "city",
        "StateName": "state",
        "ZipCode": "postal",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[@class="location-item enable-on-map enable-on-map "]')
    for d in div:

        page_url = "https://bristolcountysavings.com/locations"
        location_name = "".join(d.xpath(".//@data-title"))
        location_type = "".join(d.xpath(".//@data-types"))
        ad = "".join(d.xpath(".//@data-address"))
        a = usaddress.tag(ad, tag_mapping=tag)[0]

        street_address = (
            f"{a.get('address1')} {a.get('address2') or ''}".strip() or "<MISSING>"
        )
        city = "".join(a.get("city")) or "<MISSING>"
        state = "".join(a.get("state")) or "<MISSING>"
        postal = "".join(a.get("postal")) or "<MISSING>"
        country_code = "US"
        latitude = "".join(d.xpath(".//@data-lat")) or "<MISSING>"
        longitude = "".join(d.xpath(".//@data-lng")) or "<MISSING>"
        phone = "".join(d.xpath(".//@data-phone")) or "<MISSING>"
        hours_of_operation = "".join(d.xpath(".//@data-lobby-hours")) or "<MISSING>"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
