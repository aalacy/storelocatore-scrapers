from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.acura.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://owners.acura.com/service-maintenance/dealer-search",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }

    session = SgRequests()
    r = session.get(
        f"https://owners.acura.com/service-maintenance/dealer-search?zip={zips}&searchRadius=1000&filters=",
        headers=headers,
    )
    try:
        js = r.json()["Dealers"]
    except:
        return

    for j in js:

        page_url = j.get("Url") or "https://www.acura.com/dealer-locator-inventory"
        a = j.get("Address")
        location_name = j.get("Name") or "<MISSING>"
        street_address = a.get("AddressLine1") or "<MISSING>"
        city = a.get("City") or "<MISSING>"
        state = a.get("State") or "<MISSING>"
        postal = a.get("Zip") or "<MISSING>"
        country_code = "US"
        phone = j.get("Phone") or "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        store_number = j.get("DealerId") or "<MISSING>"
        tmp = []
        tmp_hours = []
        location_type = "<MISSING>"
        types = j.get("Departments")
        if types:
            for t in types:
                typ = t.get("Type")
                line = f"{typ}"
                tmp.append(line)
                if typ == "Sales":
                    hours = t.get("OperationHours")
                    for h in hours:
                        day = h.get("Day")
                        times = h.get("Hours")
                        lin = f"{day} {times}"
                        tmp_hours.append(lin)
                    hours_of_operation = "; ".join(tmp_hours)
            location_type = ", ".join(tmp)

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
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    zips = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=80,
        expected_search_radius_miles=80,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in zips}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
