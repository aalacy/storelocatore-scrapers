from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.deutschepost.de/"
    api_url = f"https://www.deutschepost.de/int-postfinder/standortfinder-webservice/rest/v1/nearbySearch?address={str(lat)},{str(long)}&locationType=RETAIL_OUTLET&locationType=POSTBANK_FINANCE_CENTER"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["pfLocations"]

    for j in js:

        page_url = "https://www.deutschepost.de/de/s/standorte.html"
        location_name = j.get("locationName") or "<MISSING>"
        street_address = (
            f"{j.get('street')} {j.get('houseNo')}".replace("None", "").strip()
            or "<MISSING>"
        )
        city = j.get("city") or "<MISSING>"
        postal = j.get("zipCode") or "<MISSING>"
        country_code = "DE"
        latitude = j.get("geoPosition").get("latitude")
        longitude = j.get("geoPosition").get("longitude")
        hours_of_operation = "<MISSING>"
        location_type = j.get("locationType") or "<MISSING>"
        hours = j.get("pfTimeinfos")
        tmp = []
        if hours:
            for h in hours:
                typ = h.get("type")
                if typ != "OPENINGHOUR":
                    continue
                opens = h.get("timefrom")
                closes = h.get("timeto")
                day = (
                    str(h.get("weekday"))
                    .replace("1", "Monday")
                    .replace("2", "Tuesday")
                    .replace("3", "Wednesday")
                    .replace("4", "Thursday")
                    .replace("5", "Friday")
                    .replace("6", "Saturday")
                    .replace("7", "Sunday")
                )
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=SgRecord.MISSING,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=SgRecord.MISSING,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.GERMANY],
        max_search_distance_miles=250,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID({SgRecord.Headers.STREET_ADDRESS, SgRecord.Headers.LATITUDE}),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        fetch_data(writer)
