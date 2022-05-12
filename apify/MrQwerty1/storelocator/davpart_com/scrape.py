from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_params():
    params = []
    types = ["office", "retail", "residential", "industrial"]
    r = session.get(
        "https://davpartcorp.mallmaverick.com/api/v4/davpartcorp/child_properties.json",
        headers=headers,
    )
    cats = r.json()["categories"]
    for _type in types:
        slugs = cats[_type]
        for slug in slugs:
            params.append((_type, slug))

    return params


def get_data(param, sgw: SgWriter):
    location_type, slug = param
    api = f"https://davpartcorp.mallmaverick.com/api/v4/{slug}/all.json"
    page_url = f"https://davpart.com/{location_type}/{slug}"
    r = session.get(api, headers=headers)
    j = r.json()["property"]

    adr1 = j.get("address1") or ""
    adr2 = j.get("address2") or ""
    street_address = f"{adr1} {adr2}".strip()
    city = j.get("city")
    state = j.get("province_state")
    postal = j.get("postal_code")
    country_code = j.get("country")
    location_name = j.get("name")
    phone = j.get("contact_phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        latitude=latitude,
        longitude=longitude,
        location_type=location_type,
        phone=phone,
        locator_domain=locator_domain,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    params = get_params()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {
            executor.submit(get_data, param, sgw): param for param in params
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://davpart.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
