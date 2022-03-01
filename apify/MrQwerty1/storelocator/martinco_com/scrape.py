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
        "https://www.martinco.com/estate-agents-and-letting-agents?location=&sort-by=name-asc&per-page=300"
    )
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='button btn-tertiary' and contains(text(), 'Branch')]/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"{locator_domain}{slug}".replace("//", "/").replace("https:", "https:/")
    if "#" in page_url:
        page_url = page_url.split("#")[0]
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'RealEstateAgent')]/text()"))
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = j.get("branchcode")
    location_name = j.get("name") or ""
    location_name = location_name.replace("&#039;", "'").replace("&amp;", "&")
    hours = j.get("openingHours") or ""
    hours_of_operation = "".join(hours)

    a = j.get("address") or {}
    street_address = a.get("streetaddress") or ""
    street_address = street_address.replace("&#039;", "'")
    city = a.get("addresslocality") or ""
    city = city.replace("&#039;", "'")
    state = a.get("addressregion") or ""
    postal = a.get("postalcode")
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

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

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.martinco.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
