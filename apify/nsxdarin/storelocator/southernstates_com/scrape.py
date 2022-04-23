from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.southernstates.com"

    session = SgRequests()

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.southernstates.com",
        "Connection": "keep-alive",
        "Referer": "https://www.southernstates.com/farm-store/store-locator?address=1200%20ALVERSER%20DR",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }

    json_data = {
        "sort": {
            "_geo_distance": {
                "store.latlong": {
                    "lat": f"{str(lat)}",
                    "lon": f"{str(long)}",
                },
                "order": "asc",
                "unit": "km",
            },
        },
        "query": {
            "bool": {
                "must": {
                    "query_string": {
                        "query": "+live:true +(conhost:4ede55af-83ba-47d8-b537-0bca4b7a3058 conhost:SYSTEM_HOST)",
                    },
                },
                "filter": [
                    {
                        "term": {
                            "store.webPublish": "1",
                        },
                    },
                    {
                        "geo_distance": {
                            "distance": "750000miles",
                            "store.latlong": {
                                "lat": f"{str(lat)}",
                                "lon": f"{str(long)}",
                            },
                        },
                    },
                ],
            },
        },
        "size": 200,
    }

    r = session.post(
        "https://www.southernstates.com/api/es/search?pretty",
        headers=headers,
        json=json_data,
    )

    js = r.json()["contentlets"]

    for j in js:

        location_name = j.get("storeNamePublicFacing") or "<MISSING>"
        street_address = (
            f"{j.get('address1')} {j.get('address2')}".replace("None", "")
            .replace("West Park Shopping Center", "")
            .strip()
        )
        city = j.get("city") or "<MISSING>"
        state = j.get("stateAbbr") or "<MISSING>"
        postal = j.get("zipcode") or "<MISSING>"
        country_code = "US"
        phone = j.get("phone") or "<MISSING>"
        try:
            latitude = str(j.get("latlong")).split(",")[0].strip()
            longitude = str(j.get("latlong")).split(",")[1].strip()
        except:
            latitude, longitude = "<MISSING>", "<MISSING>"
        store_number = j.get("storeNumber") or "<MISSING>"
        page_url = (
            f"https://www.southernstates.com/farm-store/store-locations/{store_number}"
        )
        location_type = j.get("storeType") or "<MISSING>"
        days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]
        tmp = []
        for d in days:
            day = d
            opens = j.get(f"storeOpen{d}")
            if str(opens).find(" ") != -1:
                opens = str(opens).split()[1].replace(":00.0", "").strip()
            closes = j.get(f"storeClose{d}")
            if str(closes).find(" ") != -1:
                closes = str(closes).split()[1].replace(":00.0", "").strip()
            line = f"{day} {opens} - {closes}"
            tmp.append(line)
        hours_of_operation = "; ".join(tmp) or "<MISSING>"

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
    coords = DynamicGeoSearch(
        country_codes=[SearchableCountries.USA],
        max_search_distance_miles=100,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
