import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    urls = []
    start = [
        "https://www.newlook.com/row/sitemap",
        "https://www.newlook.com/uk/sitemap",
    ]
    for st in start:
        r = session.get(st)
        tree = html.fromstring(r.text)
        urls += tree.xpath(
            "//h3[text()='Stores']/following-sibling::ul[1]//a[not(contains(text(), 'CLOSED'))]/@href"
        )

    return urls


def get_data(page_url, sgw: SgWriter):
    if page_url.lower().find("closed") != -1:
        return

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[@id='store-hours']/text()"))
    if not text:
        return

    j = json.loads(text)
    location_name = j.get("name").replace("&#39;", "'")
    a = j.get("address") or {}
    line = (
        "".join(tree.xpath("//p[@class='store-results__address']/text()"))
        .replace("&#39;", "'")
        .strip()
    )
    city = a.get("addressLocality") or ""
    try:
        street_address = line.split(f", {city},")[0].strip()
    except:
        street_address = a.get("streetAddress") or ""

    street_address = street_address.replace(", Speke", "").replace(", Skelmersdale", "")
    state = a.get("addressRegion") or []
    state = "".join(state)
    postal = a.get("postalCode")
    country_code = a.get("addressCountry") or "United Kingdom"

    if "," in location_name:
        location_name = location_name.split(",")[0].strip()
    store_number = page_url.split("-")[-1]
    phone = j.get("telephone")
    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")
    location_type = SgRecord.MISSING

    _tmp = []
    hours = j.get("openingHoursSpecification") or []

    for h in hours:
        day = h.get("dayOfWeek").split("/")[-1]
        start = h.get("opens")
        close = h.get("closes")
        if start != close:
            _tmp.append(f"{day}: {start} - {close}")
        else:
            _tmp.append(f"{day}: Closed")

    hours_of_operation = ";".join(_tmp)
    message = "".join(tree.xpath("//p[@class='store-results__message']/text()")).strip()
    if message.lower().find("closed") != -1:
        if "permanently" in message.lower():
            return
        location_type = message

    if tree.xpath("//p[text()='Coming Soon']"):
        location_type = "Coming Soon"

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city.replace("&#39;", "'"),
        state=state,
        zip_postal=postal,
        country_code=country_code,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude,
        phone=phone,
        store_number=store_number,
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
    locator_domain = "https://www.newlook.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
