import json
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


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//div[@data-eb-locations]/@data-eb-locations"))
    js = json.loads(text)
    divs = tree.xpath("//div[@class='ae-acf-repeater-item']")
    coords = dict()

    for j in js:
        lat = j.get("lat")
        lng = j.get("lng")
        key = str(j.get("title")).lower()
        coords[key] = (lat, lng)

    for d in divs:
        location_name = "".join(d.xpath(".//h3/text()")).strip()
        line = d.xpath(".//h4/following-sibling::p[1]//text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        street_address, city, state, postal = get_address(raw_address)
        country_code = "US"
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        key = location_name.lower()
        latitude, longitude = coords.get(key)

        _tmp = []
        hours = d.xpath(".//p/strong")
        for h in hours:
            day = "".join(h.xpath("./text()")).strip()
            inter = "".join(h.xpath("./following-sibling::text()[1]")).strip()
            _tmp.append(f"{day} {inter}")

        hours_of_operation = ";".join(_tmp)

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
    locator_domain = "https://jamesconeyisland.com/"
    page_url = "https://jamesconeyisland.com/locations/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
