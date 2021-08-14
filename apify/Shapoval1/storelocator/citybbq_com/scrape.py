from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from concurrent import futures


def get_hours(hours) -> str:
    tmp = []
    for h in hours:
        day = h.get("weekday")
        start = "".join(h.get("start")).split()[1].strip()
        end = "".join(h.get("end")).split()[1].strip()
        line = f"{day} {start} - {end}"
        tmp.append(line)
    hours_of_operation = ";".join(tmp) or "<MISISNG>"
    return hours_of_operation


def get_data(coords, sgw: SgWriter):
    lat, long = coords
    locator_domain = "https://www.citybbq.com"
    api_url = f"https://nomnom-prod-api.citybbq.com/restaurants/near?lat={str(lat)}&long={str(long)}&radius=20000&limit=100&nomnom=calendars&nomnom_calendars_from=20210809&nomnom_calendars_to=20210817&nomnom_exclude_extref=999"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.citybbq.com/",
        "ui-cache-ttl": "300",
        "ui-transformer": "restaurants",
        "clientid": "citybbq",
        "Content-Type": "application/json",
        "nomnom-platform": "web",
        "Origin": "https://www.citybbq.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["restaurants"]
    s = set()
    for j in js:

        page_url = j.get("url")
        location_name = j.get("storename")
        street_address = j.get("streetaddress")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = "<MISSING>"
        try:
            hours = j.get("calendars").get("calendar")[0].get("ranges") or "<MISSING>"
        except:
            hours = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = str(get_hours(hours))
        line = latitude
        if line in s:
            continue
        s.add(line)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)

    api_url = "https://nomnom-prod-api.citybbq.com/restaurants/near?lat=13.49&long=144.78&radius=20&limit=6&nomnom=calendars&nomnom_calendars_from=20210810&nomnom_calendars_to=20210818&nomnom_exclude_extref=999"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://www.citybbq.com/",
        "ui-cache-ttl": "300",
        "ui-transformer": "restaurants",
        "clientid": "citybbq",
        "Content-Type": "application/json",
        "nomnom-platform": "web",
        "Origin": "https://www.citybbq.com",
        "Connection": "keep-alive",
        "TE": "Trailers",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }

    session = SgRequests()

    r = session.get(api_url, headers=headers)

    js = r.json()["restaurants"]
    s = set()
    for j in js:

        page_url = j.get("url")
        location_name = j.get("storename")
        street_address = j.get("streetaddress")
        city = j.get("city")
        state = j.get("state")
        postal = j.get("zip")
        country_code = j.get("country")
        phone = j.get("telephone")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = "<MISSING>"
        try:
            hours = j.get("calendars").get("calendar")[0].get("ranges") or "<MISSING>"
        except:
            hours = "<MISSING>"
        if hours != "<MISSING>":
            hours_of_operation = str(get_hours(hours))
        line = latitude
        if line in s:
            continue
        s.add(line)

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
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
        max_search_distance_miles=500000,
        expected_search_radius_miles=100,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
