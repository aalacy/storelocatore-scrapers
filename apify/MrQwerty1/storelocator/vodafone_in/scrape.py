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

    return street_address


def fetch_data(coords, sgw: SgWriter):
    lat, lng = coords
    api = f"https://www.myvi.in/bin/getStoreLocations?userlat={lat}&userlong={lng}"
    r = session.get(api, headers=headers)
    js = json.loads(r.json()["DXLSTOREDETAILS"])["storelist"]

    for j in js:
        g = j.get("geographicLocationRefOrValue") or {}
        location_name = g.get("name") or ""
        try:
            latitude = g["coordinates"][0]["latitude"]
            longitude = g["coordinates"][0]["longitude"]
        except:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

        raw_address = j.get("oldAddressFreeText") or ""
        street_address = get_international(raw_address)
        postal = j.get("locality")
        city = j.get("city")
        state = j.get("circle")

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
        closed = j.get("closedOn") or ""
        ex = ""
        if "on" in closed:
            ex = closed.split()[-1]
        start = j.get("openTime")
        end = j.get("closeTime")
        for day in days:
            if day != ex:
                _tmp.append(f"{day}: {start}-{end}")

        hours_of_operation = ";".join(_tmp)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="IN",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    locator_domain = "https://www.myvi.in/"
    page_url = SgRecord.MISSING
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.INDIA],
        expected_search_radius_miles=50,
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
