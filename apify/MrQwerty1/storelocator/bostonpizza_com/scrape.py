from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_ids():
    params = []
    r = session.get(
        "https://bostonpizza.com/content/bostonpizza/en/locations/jcr:content/root/container_73434033/map.getAllRestaurants.json",
        headers=headers,
    )
    js = r.json()["map"]["response"]
    for j in js:
        _id = j.get("identifier")
        slug = j.get("restaurantPage")
        params.append((_id, slug))

    return params


def get_data(params, sgw: SgWriter):
    store_number, slug = params
    api = f"https://bostonpizza.com/content/bostonpizza/en/locations/stavanger/jcr:content/root/container/restaurantdetails.GetDetails.{store_number}.json"
    page_url = f"https://bostonpizza.com{slug}.html"
    r = session.get(api, headers=headers)
    j = r.json()["map"]["response"]

    location_name = j.get("restaurantName")
    street_address = j.get("address")
    city = j.get("city")
    state = j.get("province")
    postal = j.get("postalCode")
    country = j.get("country")
    phone = j.get("restaurantPhoneNumber")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    _tmp = []
    hours = j.get("restaurantHours") or []
    days = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    for h in hours:
        index = h.get("DayOfWeek") or "0"
        day = days[int(index) - 1]
        if h.get("IsClosed"):
            _tmp.append(f"{day}: Closed")
            continue
        start = str(h.get("TimeOpen")).rsplit(":00", 1).pop(0)
        end = str(h.get("TimeClose")).rsplit(":00", 1).pop(0)
        _tmp.append(f"{day}: {start}-{end}")
    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country,
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_ids()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://bostonpizza.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
        "Accept": "*/*",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://bostonpizza.com/en/locations.html",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
