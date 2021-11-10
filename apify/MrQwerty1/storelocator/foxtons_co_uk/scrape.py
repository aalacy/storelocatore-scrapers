import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.foxtons.co.uk/sitemap_offices.xml")
    tree = html.fromstring(r.content)

    return tree.xpath("//loc[contains(text(), '_estate_agents.html')]/text()")


def get_without_schema(tree, page_url, sgw):
    location_name = "".join(
        tree.xpath("//h1[@class='responsive_heading']/text()")
    ).strip()
    phone = "".join(tree.xpath("//span[@class='telephone']/text()")).strip()

    _tmp = []
    tr = tree.xpath(
        "//h3[contains(text(), 'hours')]/following-sibling::table//tr[./td]"
    )
    for t in tr:
        day = "".join(t.xpath("./td[1]//text()")).strip()
        inter = "".join(t.xpath("./td[2]//text()")).strip()
        _tmp.append(f"{day}: {inter}")

    hours_of_operation = ";".join(_tmp)

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        country_code="GB",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    try:
        tree = html.fromstring(r.text)
    except:
        return

    text = "".join(tree.xpath("//script[contains(text(), 'RealEstateAgent')]/text()"))
    if not text:
        get_without_schema(tree, page_url, sgw)
        return
    j = json.loads(text)

    location_type = j.get("@type")
    store_number = j.get("branchCode")
    location_name = j.get("name") or ""
    hours_of_operation = j.get("openingHours")

    a = j.get("address") or {}
    street_address = a.get("streetAddress") or ""
    city = a.get("addressLocality") or ""
    state = a.get("addressRegion")
    postal = a.get("postalCode")
    phone = j.get("telephone")

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")

    row = SgRecord(
        page_url=page_url,
        location_name=location_name.replace("&amp;", "&").replace("&#39;", "'"),
        street_address=street_address.replace("&#39;", "'"),
        city=city.replace("&amp;", "&").replace("&#39;", "'"),
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
    locator_domain = "https://www.foxtons.co.uk"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
