import gzip
import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.decathlon.ru/sitemap-magasin-ru.xml.gz")
    tree = html.fromstring(gzip.decompress(r.content))

    return set(tree.xpath("//loc/text()"))


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(
        tree.xpath("//script[contains(text(), 'SportingGoodsStore')]/text()")
    )
    j = json.loads(text)

    location_name = "Decathlon"
    hours_of_operation = j.get("openingHours")

    a = j.get("address") or {}
    street_address = a.get("streetAddress") or ""
    if "@" in street_address:
        street_address = street_address.split(", ")[0].strip()
    if "<br>" in street_address:
        street_address = street_address.split("<br>")[0].strip()
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude") or ""
    longitude = g.get("longitude") or ""
    if len(latitude) <= 3:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="RU",
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
    locator_domain = "https://www.decathlon.ru/"
    session = SgRequests(proxy_country="ru")
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
