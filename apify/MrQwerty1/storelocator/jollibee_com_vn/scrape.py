import time
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city or ""
    state = adr.state
    postal = adr.postcode

    return street_address, city, state, postal


def get_ids():
    ids = set()
    r = session.get("https://jollibee.com.vn/api/area/0", headers=headers)
    for j in r.json()["districts"]:
        ids.add(j["id"])

    return ids


def get_en(text):
    return text.split("[:en]")[1].replace("[:]", "")


def get_vn(text):
    return text.split("[:vn]")[1].replace("[:en]", "").replace("[:]", "")


def get_data(store_number, sgw: SgWriter):
    api = f"https://jollibee.com.vn/api/store/{store_number}"
    r = session.get(api, headers=headers)
    try:
        time.sleep(2)
        j = r.json()[0]
    except:
        return

    title = j.get("title") or ""
    location_name = get_en(title)
    if not location_name:
        try:
            location_name = get_vn(title)
        except:
            return
    adr = j.get("address") or ""
    raw_address = get_en(adr)
    if not raw_address:
        raw_address = get_vn(raw_address)
    street_address, city, state, postal = get_international(raw_address)
    if city == "":
        city = raw_address.split(", ")[-1]

    latitude = j.get("lat")
    longitude = j.get("lng")
    hours = j.get("hour") or ""
    hours_of_operation = get_en(hours)
    if not hours_of_operation:
        hours_of_operation = get_vn(hours)

    row = SgRecord(
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code="VN",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
        raw_address=raw_address,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    ids = get_ids()

    with futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_url = {executor.submit(get_data, _id, sgw): _id for _id in ids}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://jollibee.com.vn/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        fetch_data(writer)
