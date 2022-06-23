from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    r = session.get(
        "https://www.dontbebroke.com/sitemap/sitemap-0.xml", headers=headers
    )
    tree = html.fromstring(r.content)
    links = tree.xpath("//loc/text()")
    for link in links:
        if "/locations/" not in link or link.endswith("/apply"):
            continue
        slug = link.split("/")[-1]
        url = f"https://www.dontbebroke.com/page-data/locations/{slug}/page-data.json"
        urls.add(url)

    return urls


def get_data(api, sgw: SgWriter):
    r = session.get(api, headers=headers)
    j = r.json()["result"]["data"]["location"]["location"]

    street_address = f'{j.get("address")} {j.get("address2") or ""}'.strip()
    city = j.get("city")
    state = j.get("state")
    postal = j.get("postalCode")
    page_url = api.replace("/page-data", "").replace(".json", "")
    location_name = "Dollar Loan Center"
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

    for d in days:
        time = j.get(d.lower())
        _tmp.append(f"{d}: {time}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="US",
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.dontbebroke.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
