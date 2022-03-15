import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    r = session.get(locator_domain, headers=headers)
    tree = html.fromstring(r.text)

    return zip(tree.xpath("//span/@data-glf-ruid"), tree.xpath("//h3/text()"))


def get_data(params, sgw: SgWriter):
    store_number, location_name = params
    data = {
        "#": None,
        "restaurant_uid": store_number,
        "payload": {
            "language_code": "en",
            "init": 1,
            "source": "website",
            "reference": None,
        },
    }

    r = session.post(
        "https://www.foodbooking.com/api/cart/init",
        headers=headers,
        data=json.dumps(data),
    )
    j = r.json()["restaurant"]

    a = j.get("restaurantAccount") or {}
    street_address = a.get("street")
    city = a.get("city")
    state = a.get("state_code")
    postal = a.get("zipcode")
    location_type = a.get("type")
    phone = j.get("phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")
    raw_address = j.get("address")

    _tmp = []
    days = {
        64: "monday - thursday",
        48: "friday - saturday",
        15: "sunday",
        79: "monday - thursday, sunday",
    }
    hours = j.get("opening_hours") or []
    for h in hours:
        _type = h.get("type")
        if _type != "opening":
            continue

        ss = h.get("begin_minute")
        es = h.get("end_minute")
        if not ss or not es:
            continue

        start = f"{ss//60}:{str(ss%60).zfill(2)}"
        end = f"{es//60}:{str(es%60).zfill(2)}"
        day = days.get(h.get("day_of_week"))

        _tmp.append(f"{day}: {start}-{end}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        location_name=location_name,
        page_url=locator_domain,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        store_number=store_number,
        location_type=location_type,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://loscompadreslbc.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "application/json, text/plain, */*",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
