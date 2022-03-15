import re
from slugify import slugify
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def get_coords():
    out = dict()
    r = session.get(
        "https://locations.getsunmedhemp.com/page-data/sq/d/1092280806.json"
    )
    js = r.json()["data"]["locations"]["nodes"]
    for j in js:
        key = slugify(str(j.get("street")))
        lat = j.get("lat") or SgRecord.MISSING
        lng = j.get("lon") or SgRecord.MISSING
        out[key] = (lat, lng)

    return out


def get_urls():
    urls = []
    r = session.get(
        "https://locations.getsunmedhemp.com/page-data/index/page-data.json"
    )
    states = r.json()["result"]["data"]["states"]["nodes"]
    for s in states:
        state = s.get("slug")
        r = session.get(
            f"https://locations.getsunmedhemp.com/page-data/{state}/page-data.json"
        )
        js = r.json()["result"]["data"]["locations"]["nodes"]
        for j in js:
            slug = j.get("slug")
            urls.append(
                f"https://locations.getsunmedhemp.com/page-data{slug}page-data.json"
            )

    return urls


def get_data(api, sgw: SgWriter):
    r = session.get(api)
    try:
        j = r.json()["result"]["data"]["location"]
    except:
        return

    page_url = api.replace("/page-data", "").replace(".json", "")
    location_name = j.get("name")
    city = j.get("city")
    street_address = j.get("street") or ""
    key = slugify(street_address)
    latitude, longitude = coords.get(key) or (SgRecord.MISSING, SgRecord.MISSING)
    postal = j.get("postal_code") or ""
    street_address = " ".join(street_address.split())
    if f"{city}," in street_address:
        if not postal:
            postal = re.findall(r"\d{5}", street_address).pop()
        street_address = street_address.split(f"{city},")[0].strip()
    state = j.get("state_code")

    store_number = j.get("storeIdentifier")
    phone = j.get("phone")

    _tmp = []
    hours = j.get("hours") or dict()
    for day, inter in hours.items():
        _tmp.append(f"{day.capitalize()}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        store_number=store_number,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://cbdrx4u.com/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "*/*",
    }
    session = SgRequests()
    coords = get_coords()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
