from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    ids = set()
    r = session.get(
        "http://www.gulftankstationsenviemretail.nl/wp-content/themes/gulf-stations/gulf-map/json.php"
    )
    js = r.json()

    for j in js:
        _id = j.get("id")
        if _id:
            ids.add(_id)

    return ids


def get_data(store_number, sgw: SgWriter):
    api = f"http://www.gulftankstationsenviemretail.nl/wp-content/themes/gulf-stations/gulf-map/json.php?station_id={store_number}"
    r = session.get(api, headers=headers)
    j = r.json()["info"]

    location_name = j.get("name")
    adr1 = j.get("street") or ""
    adr2 = j.get("house_number") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = j.get("city")
    postal = j.get("postal_code")
    country_code = "NL"
    phone = j.get("phone")
    latitude = j.get("x-cords")
    longitude = j.get("y-cords")

    _tmp = []
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    for day in days:
        start = j.get(f"open_{day}_from")
        end = j.get(f"open_{day}_till")
        if start and not end:
            _tmp.append(f"{day.capitalize()}: {start}")
            continue
        if not start and not end:
            continue
        _tmp.append(f"{day.capitalize()}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = page_url = "http://www.gulftankstationsenviemretail.nl/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
