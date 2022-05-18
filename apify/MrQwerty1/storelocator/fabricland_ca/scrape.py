from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def get_cities(state):
    data = {
        "action": "stores-by-region",
        "region": state,
        "lang": "en",
    }

    r = session.post(api, data, headers=headers)
    return r.json()["stores"].keys()


def get_states():
    data = {
        "action": "all-stores",
        "lang": "en",
    }
    r = session.post(api, data=data, headers=headers)
    return r.json()["stores"].keys()


def get_ids():
    ids = set()
    for state in get_states():
        for city in get_cities(state):
            data = {
                "action": "stores-by-city",
                "region": state,
                "city": city,
                "lang": "en",
            }
            r = session.post(api, data=data, headers=headers)
            js = r.json()["stores"]

            for j in js:
                ids.add(j.get("id"))

    return ids


def get_data(store_number, sgw: SgWriter):
    data = {
        "action": "get-store",
        "lang": "en",
        "id": store_number,
    }
    r = session.post(api, data=data, headers=headers)
    j = r.json()["store"]

    location_name = j.get("translated_name")
    page_url = f"https://fabricville.com/pages/store-details/{store_number}"
    raw_address = j.get("maps_address")
    street_address, city, state, postal = get_international(raw_address)
    country_code = "CA"
    phone = j.get("phone")
    latitude = j.get("lat")
    longitude = j.get("lng")

    _tmp = []
    h = j.get("opening_hours") or {}
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    for day in days:
        inter = h.get(day)
        _tmp.append(f"{day.capitalize()}: {inter}")
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        raw_address=raw_address,
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
    locator_domain = "https://fabricville.com/"
    api = "https://app.fabricville.com/api/store-locator/ajax"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://fabricville.com",
        "Connection": "keep-alive",
        "Referer": "https://fabricville.com/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
