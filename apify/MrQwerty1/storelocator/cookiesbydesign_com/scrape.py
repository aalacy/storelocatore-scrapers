import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_tree(url):
    r = session.get(url, headers=headers)
    if r.status_code == 404:
        return html.fromstring("<html>")
    return html.fromstring(r.content)


def get_urls():
    root = get_tree("https://www.cookiesbydesign.com/locationsitemap.aspx")
    return root.xpath("//ul[@id='ShoppeColumn']/li//a/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.cookiesbydesign.com{slug}"
    tree = get_tree(page_url)
    text = "".join(tree.xpath("//script[contains(text(), 'Bakery')]/text()")).strip()
    if not text:
        return
    j = json.loads(text)

    location_name = "".join(tree.xpath("//h1/text()")).strip()
    a = j.get("address")
    street_address = a.get("streetAddress")
    city = str(a.get("addressLocality")).split(",")[0].strip()
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    country_code = a.get("addressCountry")
    phone = j.get("telephone")
    store_number = page_url.split("_")[-1].replace(".aspx", "")

    g = j.get("geo")
    latitude = g.get("latitude") or ""
    longitude = g.get("longitude") or ""
    if "0.0" in latitude:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    hours = tree.xpath(
        "//b[./label[contains(text(), 'Hours')]]/following-sibling::text()"
    )
    hours = list(filter(None, [h.strip() for h in hours]))
    hours_of_operation = " ".join(";".join(hours).split())

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
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
    locator_domain = "https://unclejulios.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
