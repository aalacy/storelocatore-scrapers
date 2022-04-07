from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgpostal.sgpostal import International_Parser, parse_address
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.olivegarden.com"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.olivegarden.com",
        "Connection": "keep-alive",
        "Referer": "https://www.olivegarden.com/locations/location-search",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "max-age=0",
    }

    data = {
        "geoCode": f"{str(lat)},{str(long)}",
        "resultsPerPage": "100",
        "resultsOffset": "0",
        "pdEnabled": "",
        "reservationEnabled": "",
        "isToGo": "",
        "privateDiningEnabled": "",
        "isNew": "",
        "displayDistance": "true",
        "locale": "en_US",
    }

    r = session.post(
        "https://www.olivegarden.com/web-api/restaurants", headers=headers, data=data
    )

    js = r.json()["successResponse"]["locationSearchResult"]["Location"]
    for j in js:

        location_name = j.get("restaurantName") or "<MISSING>"
        ad = f"{j.get('AddressOne')} {j.get('AddressTwo')}".strip() or "<MISSING>"
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        if street_address == "<MISSING>" or street_address.isdigit():
            street_address = (
                f"{j.get('AddressOne')} {j.get('AddressTwo')}".strip() or "<MISSING>"
            )
        city = j.get("city") or "<MISSING>"
        state = j.get("state") or "<MISSING>"
        postal = j.get("zip") or "<MISSING>"
        country_code = j.get("country")
        phone = j.get("phoneNumber") or "<MISSING>"
        latitude = j.get("latitude") or "<MISSING>"
        longitude = j.get("longitude") or "<MISSING>"
        hours_of_operation = "<MISSING>"
        hours = j.get("weeklyHours")
        tmp = []
        store_number = j.get("restaurantNumber") or "<MISSING>"
        if hours:
            for h in hours:
                type_hoo = h.get("hourTypeDesc")
                if type_hoo != "Hours of Operations":
                    continue
                day = (
                    str(h.get("dayOfWeek"))
                    .replace("1", "Sunday")
                    .replace("2", "Monday")
                    .replace("3", "Tuesday")
                    .replace("4", "Wednesday")
                    .replace("5", "Thursday")
                    .replace("6", "Friday")
                    .replace("7", "Saturday")
                )
                opens = h.get("startTime")
                closes = h.get("endTime")
                line = f"{day} {opens} - {closes}"
                tmp.append(line)
            hours_of_operation = "; ".join(tmp)
        page_url = f"https://www.olivegarden.com/locations/{str(state).lower()}/{str(city).replace(' ','-').lower()}/{str(location_name).replace(' ','-').lower()}/{store_number}"

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
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
