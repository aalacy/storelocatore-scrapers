from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries


def fetch_data(sgw: SgWriter):

    coords = DynamicZipSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=500,
        expected_search_radius_miles=100,
        max_search_results=50,
    )

    session = SgRequests(verify_ssl=False)
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

    for url in coords:

        params = {
            "zip": f"{url}",
            "searchRadius": "1000",
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
            coords.found_nothing()
            continue

        for j in js:

            page_url = "https://owners.honda.com/"
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
            latitude = a.get("Latitude") or ""
            longitude = a.get("Longitude") or ""
            coords.found_location_at(latitude, longitude)
            dep = j.get("Departments")
            types = []
            for d in dep:
                t = d.get("Type")
                types.append(t)
            location_type = ", ".join(types)
            hours_of_operation = "<MISSING>"
            store_number = j.get("DealerId")
            hours = j.get("Departments")

            tmp = []
            if hours:
                for h in hours:
                    typ = h.get("Type")
                    if typ != "Sales":
                        continue
                    operation_hours = h.get("OperationHours")
                    tmp.append(typ)
                    for i in operation_hours:
                        day = i.get("Day")
                        times = i.get("Hours")
                        line = f"{day} {times}"
                        tmp.append(line)
                    hours_of_operation = (
                        "; ".join(tmp)
                        .replace("Service;", "Service")
                        .replace("Parts;", "Parts")
                        .replace("Sales;", "")
                        .strip()
                    )
            if (
                hours_of_operation == "Sales"
                or hours_of_operation == "Service"
                or hours_of_operation == "Parts"
            ):
                hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
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
            )
        if not js:
            coords.found_nothing()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
