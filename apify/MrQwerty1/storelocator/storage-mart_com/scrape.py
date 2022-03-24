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
    start_urls = [
        "https://www.storage-mart.com/sitemap/united-states",
        "https://www.storage-mart.com/sitemap/canada",
        "https://www.storage-mart.com/en-gb/sitemap/united-kingdom",
    ]

    for u in start_urls:
        r = session.get(u)
        tree = html.fromstring(r.text)

        links = tree.xpath(
            "//div[@class='col-xs-5ths']//a[@class='rnl-EditorState-Link']/@href"
        )
        for link in links:
            urls.append(f"https://www.storage-mart.com{link}")

    return urls


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(),'SelfStorage')]/text()"))
    if not text:
        return

    j = json.loads(text)
    location_name = j.get("name")
    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    g = j.get("geo") or {}
    country_code = g.get("addressCountry")
    phone = j.get("telephone")
    latitude = g.get("latitude")
    longitude = g.get("longitude")
    location_type = j.get("@type")

    _tmp = []
    line = "".join(tree.xpath("""//script[contains(text(), '"office":')]/text()"""))
    line = line.split('"office":')[1].split('"access"')[0][:-1]
    try:
        divs = json.loads(line)["hours"]
    except:
        divs = []

    for d in divs:
        day = d.get("day")
        start = d.get("open")
        close = d.get("close")
        if start == close:
            _tmp.append(f"{day}: Closed")
        else:
            _tmp.append(f"{day}: {start} - {close}")

    hours_of_operation = ";".join(_tmp).replace(".5", ":30")

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
    locator_domain = "https://www.storage-mart.com"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
