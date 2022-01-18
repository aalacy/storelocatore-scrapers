import json
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    postal = adr.postcode

    return street_address, postal


def fetch_data(coords, sgw: SgWriter):
    lat, lng = coords
    api = f"https://api.public.vodafone.co.nz/vf/public/cms-store-locator-rest/includes/lookup-json.php?lat={lat}&lng={lng}"
    r = session.get(api, headers=headers)
    text = r.text.replace("storesJSONCallback(", "").replace(");", "")
    js = json.loads(text)["markers"]

    for j in js:
        location_name = j.get("name") or ""
        if "Permanently" in location_name:
            continue
        line = j.get("mapping_address") or ""
        street_address, postal = get_international(line)
        city = j.get("town_city")
        state = j.get("suburb") or ""
        if state[0].isdigit():
            postal = state
            state = SgRecord.MISSING
        phone = j.get("phone")
        latitude = j.get("lat")
        longitude = j.get("lng")

        _tmp = []
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        for day in days:
            start = j.get(f"{day}_Open")
            end = j.get(f"{day}_Closed")
            _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)
        if "closed" in location_name.lower():
            hours_of_operation = "Closed"

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="NZ",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.vodafone.co.nz/"
    page_url = "https://www.vodafone.co.nz/help/store-locations/"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.NEW_ZEALAND],
        expected_search_radius_miles=100,
    )
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LOCATION_NAME}
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for p in search:
            fetch_data(p, writer)
