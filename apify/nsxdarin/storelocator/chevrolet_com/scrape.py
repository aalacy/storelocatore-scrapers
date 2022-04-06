from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.chevrolet.com/"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.chevrolet.com/dealer-locator",
        "clientapplicationid": "quantum",
        "content-type": "application/json; charset=utf-8",
        "locale": "en-US",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    params = {
        "desiredCount": "25",
        "distance": "500",
        "makeCodes": "001",
        "serviceCodes": "",
        "latitude": f"{str(lat)}",
        "longitude": f"{str(long)}",
        "searchType": "latLongSearch",
    }

    r = session.get(
        "https://www.chevrolet.com/bypass/pcf/quantum-dealer-locator/v1/getDealers",
        headers=headers,
        params=params,
    )

    js = r.json()["payload"]["dealers"]

    for j in js:
        a = j.get("address")
        page_url = "https://www.chevrolet.com/dealer-locator"
        location_name = j.get("dealerName")
        street_address = f"{a.get('addressLine1')} {a.get('addressLine2')} {a.get('addressLine3')}".strip()
        city = a.get("cityName") or "<MISSING>"
        state = a.get("region") or "<MISSING>"
        postal = a.get("postalCode") or "<MISSING>"
        country_code = "US"
        phone = j.get("generalContact").get("phone1") or "<MISSING>"
        latitude = j.get("geolocation").get("latitude") or "<MISSING>"
        longitude = j.get("geolocation").get("longitude") or "<MISSING>"
        store_number = j.get("dealerCode") or "<MISSING>"
        days = {
            1: "Monday",
            2: "Tuesday",
            3: "Wednesday",
            4: "Thursday",
            5: "Friday",
            6: "Saturday",
            7: "Sunday",
        }

        hours = (
            j.get("generalOpeningHour")
            or j.get("serviceOpeningHour")
            or j.get("partsOpeningHour")
        )

        hours_of_operation_tmp = []

        for hour in hours:
            for day in hour.get("dayOfWeek"):
                hours_of_operation_tmp.append(
                    f"{days[day]} {hour.get('openFrom')}-{hour.get('openTo')}"
                )
        hours_of_operation = "; ".join(hours_of_operation_tmp)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=50,
        expected_search_radius_miles=50,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
