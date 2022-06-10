from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):
    search = DynamicZipSearch(
        country_codes=[SearchableCountries.USA], expected_search_radius_miles=50
    )
    for _zip in search:
        json_data = {
            "radius": 60,
            "address": "",
            "city": "",
            "state": "",
            "zip": _zip,
            "lineOfBusinessList": [
                "AUTOP",
                "AUTOB",
                "HOME",
                "RENTER",
                "CONDO",
            ],
        }
        r = session.post(api, headers=headers, json=json_data)
        jss = r.json().get("businessUnitList")
        if not jss:
            search.found_nothing()
            continue

        js = jss[0]["agencyList"]
        if not js:
            search.found_nothing()
            continue

        for j in js:
            adr1 = j.get("addressLine1") or ""
            adr2 = j.get("addressLine2") or ""
            street_address = f"{adr1} {adr2}".strip()
            city = j.get("city")
            state = j.get("state")
            postal = j.get("zip")
            country_code = "US"
            store_number = j.get("Id")
            location_name = j.get("name") or ""
            location_name = " ".join(location_name.split())
            phone = j.get("phone")
            latitude = j.get("latitude")
            longitude = j.get("longitude")
            search.found_location_at(latitude, longitude)

            row = SgRecord(
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
                locator_domain=locator_domain,
            )

            sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.kemper.com/"
    api = "https://customer.kemper.com/faa/v1/agency/ka"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Origin": "https://customer.kemper.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
