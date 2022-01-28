from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def generate_links():
    r = session.get("https://stores.charlottetilbury.com/index.json")
    js = r.json()["directoryHierarchy"]
    urls = list(get_urls(js))

    return urls


def get_urls(states):
    for state in states.values():
        children = state["children"]
        if children is None:
            yield f"https://stores.charlottetilbury.com/{state['url']}".replace(
                ".html", ".json"
            )
        else:
            yield from get_urls(children)


def get_data(url, sgw: SgWriter):
    r = session.get(url)
    j = r.json()

    page_url = url.replace(".json", ".html")
    location_name = j.get("name")
    street_address = " ".join(f"{j.get('address1')} {j.get('address2') or ''}".split())
    city = j.get("city")
    state = j.get("state")
    postal = j.get("postalCode")
    country_code = j.get("country")
    store_number = j.get("corporateCode")
    phone = j.get("phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")
    days = j.get("hours", {}).get("days") or []

    _tmp = []
    for d in days:
        day = d.get("day")[:3].capitalize()
        try:
            interval = d.get("intervals")[0]
            start = str(interval.get("start")).zfill(4)
            end = str(interval.get("end")).zfill(4)
            line = f"{day}  {start[:2]}:{start[2:]} - {end[:2]}:{end[2:]}"
        except IndexError:
            line = f"{day}  Closed"

        _tmp.append(line)

    hours_of_operation = ";".join(_tmp) or SgRecord.MISSING
    if (
        hours_of_operation.count("Closed") == 7
        or location_name.lower().find("closed") != -1
    ):
        hours_of_operation = "Closed"

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
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = generate_links()

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://charlottetilbury.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
