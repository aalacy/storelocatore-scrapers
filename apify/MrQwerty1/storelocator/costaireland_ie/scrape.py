from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    postal = adr.postcode

    return street_address, city, postal


def fetch_data(sgw: SgWriter):
    api = "https://www.costaireland.ie/api/cf/?locale=en-IE&include=2&content_type=storeV2&limit=500"
    page_url = "https://www.costaireland.ie/locations/store-locator/map"
    r = session.get(api, headers=headers)
    js = r.json()["items"]

    for j in js:
        j = j.get("fields") or {}
        location_name = j.get("storeName")
        raw_address = j.get("storeAddress")
        street_address, city, postal = get_international(raw_address)
        country = "IE"

        loc = j.get("location") or {}
        latitude = loc.get("lat")
        longitude = loc.get("lon")

        _tmp = []
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for day in days:
            start = j.get(f"open{day}")
            end = j.get(f"close{day}")
            _tmp.append(f"{day}: {start}-{end}")
        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.costaireland.ie/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
