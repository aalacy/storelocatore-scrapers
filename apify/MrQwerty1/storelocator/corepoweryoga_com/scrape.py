from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    r = session.get("https://d7mth1zoj92fj.cloudfront.net/data/all-locations")
    js = r.json().values()
    for j in js:
        path = j.get("path")
        if path:
            urls.append(f"https://d7mth1zoj92fj.cloudfront.net/data/content{path}")

    return urls


def get_value(j, key, end_key="value"):
    try:
        value = j.get(key, {}).get("und", {}) or []
    except:
        return ""
    if value:
        return value[0].get(end_key)


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    j = r.json()

    if str(j).lower().find("coming soon") != -1:
        return

    page_url = j.get("path")
    location_name = j.get("title")
    street_address = f"{get_value(j, 'field_address_1')} {get_value(j, 'field_address_2') or ''}".strip()
    city = get_value(j, "field_city")
    state = get_value(j, "field_studio_state")
    postal = get_value(j, "field_zip_code")
    country_code = get_value(j, "field_country")
    if country_code == "USA" or country_code == "United States":
        country_code = "US"

    phone = get_value(j, "field_phone") or SgRecord.MISSING
    geo = get_value(j, "field_location", "geom")
    if geo:
        geo = geo.replace("POINT", "").replace("(", "").replace(")", "").strip().split()
        latitude = geo[1]
        longitude = geo[0]
    else:
        latitude = SgRecord.MISSING
        longitude = SgRecord.MISSING

    hours_of_operation = SgRecord.MISSING
    if phone == SgRecord.MISSING:
        hours_of_operation = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code=country_code,
        store_number=SgRecord.MISSING,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.corepoweryoga.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
