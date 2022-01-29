import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get(
        "https://www.mantruckvanandbus.co.uk/dealer-locator/", headers=headers
    )
    tree = html.fromstring(r.text)

    return tree.xpath("//a[contains(text(), 'Details')]/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.mantruckvanandbus.co.uk{slug}"
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'AutoDealer')]/text()"))
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = page_url.split("/")[-3]
    location_name = j.get("name")

    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    _tmp = []
    hours = tree.xpath(
        "//h2[contains(text(), 'Hours')]/following-sibling::div//tr[not(.//strong)]"
    )
    for h in hours:
        day = "".join(h.xpath("./td[1]/text()")).strip()
        inter = "".join(h.xpath("./td[2]/text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="GB",
        latitude=latitude,
        longitude=longitude,
        store_number=store_number,
        location_type=location_type,
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
    locator_domain = "https://www.mantruckvanandbus.co.uk/"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
