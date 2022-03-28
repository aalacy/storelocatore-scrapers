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

    try:
        a = usaddress.tag(line, tag_mapping=tag)[0]
        street_address = f"{a.get('address1')} {a.get('address2') or ''}".strip()
        if street_address == "None":
            street_address = "<MISSING>"
    except usaddress.RepeatedLabelError:
        street_address = line.split(",")[0]
        a = usaddress.tag(",".join(line.split(",")[1:]), tag_mapping=tag)[0]

    city = a.get("city")
    state = a.get("state")
    postal = a.get("postal")

    return street_address, city, state, postal


def fetch_data(sgw: SgWriter):
    api = "https://kristoil.com/wp-content/themes/krist-mar-2022/ajax/map.php"
    r = session.get(api, headers=headers)
    js = r.json().values()
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)

    for j in js:
        location_name = j.get("title")
        store_number = j.get("ID")
        phone = j.get("phone") or ""
        _id = phone[-4:]
        a = j.get("location") or {}

        li = tree.xpath(
            f"//li[@class='grid grid--locations grid--one-col-mobile locations-list__list-item' and .//a[contains(text(), '-{_id}')]]"
        )[0]

        line = (
            "".join(
                li.xpath(
                    ".//li[@class='locations-list__phone-number']/preceding-sibling::li[1]/text()"
                )
            )
            .replace(".", "")
            .strip()
        )
        street_address, city, state, postal = get_address(line)
        latitude = a.get("lat")
        longitude = a.get("lng")

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            store_number=store_number,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://kristoil.com/"
    page_url = "https://kristoil.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://kristoil.com/locations/",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "TE": "Trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
