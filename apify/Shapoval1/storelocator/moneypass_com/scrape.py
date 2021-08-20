import json
from sgzip.dynamic import SearchableCountries, DynamicZipSearch
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_data(_zip, sgw: SgWriter):
    locator_domain = "https://www.moneypass.com/"
    page_url = "https://www.moneypass.com/atm-locator.html"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json; charset=UTF-8",
        "Origin": "https://moneypas slocator.wave2.io",
        "Connection": "keep-alive",
        "Referer": "https://moneypasslocator.wave2.io/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "TE": "trailers",
    }

    data = {
        "Latitude": "",
        "Longitude": "",
        "Address": f"{_zip}",
        "City": "",
        "State": "",
        "Zipcode": "",
        "Country": "",
        "Action": "textsearch",
        "ActionOverwrite": "",
        "Filters": "ATMSF,ATMDP,HAATM,247ATM,",
    }

    session = SgRequests()
    r = session.post(
        "https://locationapi.wave2.io/api/client/getlocations",
        headers=headers,
        data=json.dumps(data),
    )
    try:
        js = r.json()["Features"]
    except:
        return
    for j in js:
        a = j.get("Properties")
        location_name = a.get("LocationName") or "<MISSING>"
        street_address = a.get("Address") or "<MISSING>"
        city = a.get("City") or "<MISSING>"
        state = a.get("State") or "<MISSING>"
        postal = a.get("Postalcode") or "<MISSING>"
        if postal == "0":
            postal = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        location_type = a.get("LocationCategory") or "<MISSING>"
        hours_of_operation = (
            j.get("LocationFeatures").get("TwentyFourHours") or "<MISSING>"
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    postals = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=40,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in postals}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
