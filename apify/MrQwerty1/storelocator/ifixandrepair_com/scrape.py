import usaddress
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


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
    street_address = f"{a.get('address1')} {a.get('address2') or ''}".replace(
        "None", ""
    ).strip()
    if street_address.startswith("Suite"):
        street_address = line

    return street_address


def fetch_data(coords, sgw):
    lat, lng = coords
    url = f"https://ifixandrepair.com/wp-admin/admin-ajax.php?action=store_search&lat={lat}&lng={lng}&search_radius=200&max_results=50"
    r = session.get(url, headers=headers)

    for j in r.json():
        location_name = j.get("store") or ""
        if "(" in location_name:
            location_name = location_name.split("(")[0].strip()
        page_url = j.get("permalink")
        line = j.get("address") or ""
        street_address = get_address(line)
        city = j.get("city") or ""
        if city.endswith(","):
            city = city[:-1]
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        store_number = j.get("id")
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        source = j.get("hours") or "<html></html>"
        tree = html.fromstring(source)
        tr = tree.xpath("//tr")
        for t in tr:
            day = "".join(t.xpath("./td[1]//text()")).strip()
            inter = "".join(t.xpath("./td[2]//text()")).strip()
            _tmp.append(f"{day}: {inter}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            store_number=store_number,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://ifixandrepair.com/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    }
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountries.USA], expected_search_radius_miles=150
        )
        for coord in search:
            fetch_data(coord, writer)
