from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_js():
    api = "https://www.benzinaorlen.cz/api/stations/list?topN=0&now=false&nonstop=false&fuelTypes=&accessoriesTypes=&gastroTypes=&paymentTypes=&carWashTypes="
    r = session.get(api, headers=headers)
    js = r.json()["stations"]

    return js


def get_data(jj, sgw: SgWriter):
    store_number = jj.get("id")
    api = f"https://www.benzinaorlen.cz/api/stations/{store_number}"
    r = session.get(api, headers=headers)
    j = r.json()

    s = j.get("station") or {}
    a = s.get("address") or {}
    location_name = s.get("name")
    location_type = s.get("type")
    street_address = a.get("streetAndNumber")
    city = a.get("city")
    country_code = "CZ"
    country = a.get("country") or ""
    if "Slo" in country:
        country_code = "SK"

    try:
        phone = s["contacts"][0]
    except IndexError:
        phone = SgRecord.MISSING

    g = jj.get("location") or {}
    latitude = g.get("lat")
    longitude = g.get("lng")

    _tmp = []
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours = s.get("openingHours") or []
    for h in hours:
        s_day = h.get("weekdayFrom") or 0
        e_day = h.get("weekdayTo") or 0
        start = h.get("from")
        end = h.get("to")
        _tmp.append(f"{days[s_day]}-{days[e_day]}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        location_type=location_type,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    js = get_js()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, j, sgw): j for j in js}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.benzinaorlen.cz/"
    page_url = "https://www.benzinaorlen.cz/stanice"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:101.0) Gecko/20100101 Firefox/101.0",
        "Accept": "application/json, text/plain, */*",
        "Connection": "keep-alive",
        "Referer": "https://www.benzinaorlen.cz/stanice",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
