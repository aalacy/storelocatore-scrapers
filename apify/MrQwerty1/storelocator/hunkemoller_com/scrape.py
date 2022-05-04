import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = set()
    api = "https://www.hunkemoller.com/on/demandware.store/Sites-hunkemoller-us-Site/en_US/Stores-GetStoresJSON"
    r = session.get(api, headers=headers)
    text = r.text.replace("][", ",")
    js = json.loads(text)

    for j in js:
        slug = j.get("storeUrlPath")
        url = f"https://www.hunkemoller.com/stores{slug}"
        urls.add(url)

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    if r.status_code != 200:
        return
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'pageContext =')]/text()")
    ).strip()
    text = text.split("pageContext =")[1].replace(";", "")
    j = json.loads(text)["analytics"]["store"]

    location_name = j.get("name")
    street_address = j.get("streetAddress")
    city = j.get("city")
    postal = j.get("postalCode")
    country_code = j.get("addressCountry")
    phone = j.get("phone")
    store_number = j.get("branchCode")
    latitude = j.get("latitude")
    longitude = j.get("longitude")

    _tmp = []
    hours = j.get("openingHours") or []
    if hours:
        for h in hours:
            day = h.get("dayOfWeek")
            start = h.get("open")
            end = h.get("close")
            _tmp.append(f"{day}: {start}-{end}")
    else:
        hours = tree.xpath("//ul[@class='b-store_details-timetable_list']/li")
        for h in hours:
            day = "".join(h.xpath("./span[1]//text()")).strip()
            inter = "".join(h.xpath("./span[2]//text()")).strip()
            _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        zip_postal=postal,
        country_code=country_code,
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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.hunkemoller.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
