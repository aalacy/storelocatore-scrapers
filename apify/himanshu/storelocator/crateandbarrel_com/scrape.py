from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from concurrent import futures


def get_data(zips, sgw: SgWriter):

    locator_domain = "https://www.crateandbarrel.com"

    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/json",
        "x-requested-with": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Referer": "https://www.crateandbarrel.com/stores/",
        "Proxy-Authorization": "Basic YWNjZXNzX3Rva2VuOjFoMmpscmczNHZrZ3NsYjhob29xZG8zZmpmYWRjaTIyZDRpamc4ZzN1MDAyYzFicWpjNms=",
        "Connection": "keep-alive",
    }

    params = {
        "searchKeyword": f"{zips}",
    }

    r = session.get(
        "https://www.crateandbarrel.com/stores/locator", headers=headers, params=params
    )
    js = r.json()["storeList"]

    for s in js:

        slug = s.get("storeUrl")
        page_url = f"https://www.crateandbarrel.com{slug}"
        location_name = s.get("storeName")
        store_number = s.get("storeNumber")
        street_address = f"{s.get('address1')} {s.get('address2')}".strip()
        city = s.get("city")
        state = s.get("state")
        postal = s.get("zip")
        location_type = "Store"
        if s.get("distributionCenter"):
            location_type = "Distribution Center"
        elif s.get("outlet"):
            location_type = "Outlet"
        elif s.get("corporate"):
            location_type = "Corporate"
        if location_type not in ["Store", "Outlet"]:
            continue
        country_code = s.get("country")
        phone = (
            f"({s.get('phoneAreaCode')}) {s.get('phonePrefix')}-{s.get('phoneSuffix')}"
        )
        latitude = s.get("storeLat")
        longitude = s.get("storeLong")
        hours = s.get("hoursStr")
        hours_of_operation = "<MISSING>"
        if hours:
            a = html.fromstring(hours)
            hours_of_operation = (
                " ".join(a.xpath("//*//text()")).replace("\n", "").strip()
            )
            hours_of_operation = " ".join(hours_of_operation.split())

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
    coords = DynamicZipSearch(
        country_codes=[SearchableCountries.USA, SearchableCountries.CANADA],
        max_search_distance_miles=70,
        expected_search_radius_miles=70,
        max_search_results=None,
    )

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in coords}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
        fetch_data(writer)
