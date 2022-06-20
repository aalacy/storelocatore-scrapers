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
    r = session.get(api, headers=headers)
    js = r.json()["Results"]

    for j in js:
        text = j.get("Html") or "<html>"
        tree = html.fromstring(text)
        line = tree.xpath("//div[@class='loc-result-card-address-container']//a/text()")
        line = list(filter(None, [li.strip() for li in line]))
        raw_address = ", ".join(line)
        street_address, city, state, postal = get_address(raw_address)
        if "," in city:
            city = city.split(",")[-1].strip()
        country_code = "US"
        store_number = j.get("Id")
        location_name = "".join(
            tree.xpath("//div[@class='loc-result-card-name']/text()")
        ).strip()
        try:
            phone = tree.xpath("//a[contains(@href, 'tel')]/text()")[0]
        except IndexError:
            phone = SgRecord.MISSING

        g = j.get("Geospatial") or {}
        latitude = g.get("Latitude")
        longitude = g.get("Longitude")

        _tmp = []
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]/text()")).strip()
            time = "".join(t.xpath("./td[2]/text()")).strip()
            _tmp.append(f"{day} {time}")

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
            store_number=store_number,
            raw_address=raw_address,
            hours_of_operation=hours_of_operation,
            locator_domain=locator_domain,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.worknetoccupationalmedicine.com/"
    page_url = "https://www.worknetoccupationalmedicine.com/find-a-location/#g=&o=Distance,Ascending"
    api = "https://www.worknetoccupationalmedicine.com//sxa/search/results/?s={47229739-6FFF-4802-8CC0-D4EB1BD20866}|{47229739-6FFF-4802-8CC0-D4EB1BD20866}&itemid={02D546B1-BD74-4AF5-8416-D0E61C36DD70}&sig=&v=%7B55BD26AB-5DEC-4454-9214-5C9AEA0EF752%7D&p=20&g=&o=Distance%2CAscending"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
