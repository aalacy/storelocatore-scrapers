from lxml import html
from concurrent import futures
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch


def get_hours(code):
    _tmp = []
    url = f"https://www.fiatcanada.com/en/dealers/{code}"

    r = session.get(url, headers=headers)
    if r.status_code == 404:
        return
    try:
        tree = html.fromstring(r.text)
    except:
        return
    divs = tree.xpath("//div[@id='sales-tab']//p[@class='C_DD-week-day']")
    for d in divs:
        day = "".join(d.xpath("./span[1]/text()")).strip()
        time = "".join(d.xpath("./span[last()]/text()")).strip()
        _tmp.append(f"{day}: {time}")

    return ";".join(_tmp)


def fetch_data(la, ln, sgw: SgWriter):
    codes = []
    hours = dict()
    api = f"https://www.fiatcanada.com/data/dealers/expandable-radius?brand=fiat&longitude={ln}&latitude={la}&radius=200"

    r = session.get(api, headers=headers)
    js = r.json()["dealers"]
    for j in js:
        codes.append(j.get("code"))

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_hours, code): code for code in codes}
        for future in futures.as_completed(future_to_url):
            time = future.result()
            code = future_to_url[future]
            hours[code] = time

    for j in js:
        street_address = j.get("address")
        city = j.get("city")
        state = j.get("province")
        postal = j.get("zipPostal")
        country_code = "CA"
        store_number = j.get("code")
        page_url = f"https://www.fiatcanada.com/en/dealers/{store_number}"
        location_name = j.get("name")
        phone = j.get("contactNumber")
        latitude = j.get("latitude")
        longitude = j.get("longitude")
        hours_of_operation = hours.get(store_number)

        row = SgRecord(
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
            latitude=str(latitude),
            longitude=str(longitude),
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "ru,en-US;q=0.7,en;q=0.3",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
    locator_domain = "https://www.fiatcanada.com/"
    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA], expected_search_radius_miles=100
    )
    with SgWriter(
        SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for lat, lng in search:
            fetch_data(lat, lng, writer)
