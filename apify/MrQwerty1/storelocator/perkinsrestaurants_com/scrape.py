from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.perkinsrestaurants.com/sitemap.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '/locations/')]/text()")


def get_data(page_url, sgw: SgWriter):
    if page_url.endswith("/locations/"):
        return

    slug = page_url.split("/")[-2]
    api = f"https://www.perkinsrestaurants.com/_data/locations/{slug}.json"
    r = session.get(api)
    j = r.json()
    path = j.get("path")
    location_name = j.get("name")
    j = j["content"]

    page_url = f"{locator_domain}{path}"
    street_address = j.get("address")
    city = j.get("city")
    state = j.get("state")
    postal = j.get("zipcode")
    country_code = j.get("country")
    store_number = j.get("store_num")
    phone = j.get("phone")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    _tmp = []
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    hours = j.get("hours") or []
    if hours:
        hours = hours[0]
        for d in days:
            part = d.lower()[:3]
            start = hours.get(f"{part}_open")
            if not start:
                continue
            end = hours.get(f"{part}_close")

            if start == end:
                _tmp.append(f"{d}: Closed")
            else:
                _tmp.append(f"{d}: {start} - {end}")

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
        phone=phone,
        latitude=latitude,
        longitude=longitude,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.perkinsrestaurants.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
