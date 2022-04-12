from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://honda.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Referer": "https://owners.honda.com/service-maintenance/dealer-search",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    params = {
        "zip": f"{zips}",
        "searchRadius": "",
        "filters": "",
    }

    r = session.get(
        "https://owners.honda.com/service-maintenance/dealer-search",
        headers=headers,
        params=params,
    )
    try:
        js = r.json()["Dealers"]
    except:
        return

    for j in js:

        page_url = "https://mcdonalds.es/restaurantes"
        a = j.get("Address")
        location_name = j.get("Name") or "<MISSING>"
        street_address = (
            f"{a.get('AddressLine1')} {a.get('AddressLine2') or ''}".replace(
                "None", ""
            ).strip()
        )
        city = a.get("City")
        state = a.get("State")
        postal = a.get("Zip")
        country_code = "US"
        phone = j.get("Phone") or "<MISSING>"
        latitude = a.get("Latitude") or "<MISSING>"
        longitude = a.get("Longitude") or "<MISSING>"
        dep = j.get("Departments")
        types = []
        for d in dep:
            t = d.get("Type")
            types.append(t)
        location_type = ", ".join(types)
        hours_of_operation = "<MISSING>"
        store_number = j.get("DealerId")
        hours = j.get("Departments")[0].get("OperationHours")
        tmp = []
        if hours:
            for h in hours:
                day = h.get("Day")
                times = h.get("Hours")
                line = f"{day} {times}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)

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
    coords = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=200,
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
