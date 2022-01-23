import json
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.nandos.sa/eat/restaurants/all")
    tree = html.fromstring(r.text)

    return tree.xpath("//a[@class='link']/@href")


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.nandos.sa{slug}"
    r = session.get(page_url, headers=headers)
    source = r.text.replace("<!--//--><![CDATA[//><!--", "").replace("//--><!]]>", "")
    tree = html.fromstring(source)
    text = "".join(tree.xpath("//script[contains(text(), 'Restaurant')]/text()"))
    j = json.loads(text)

    location_type = j.get("@type")
    location_name = j.get("name")
    hours_of_operation = j.get("openingHours") or []
    hours_of_operation = "".join(hours_of_operation)

    a = j.get("address") or {}
    street_address = a.get("streetAddress")
    city = a.get("addressLocality")
    state = a.get("addressRegion")
    postal = a.get("postalCode")

    try:
        phone = j["contactPoint"][0]["telephone"].replace("+", "")
        if phone.startswith("44"):
            phone = phone[2:]
    except:
        phone = SgRecord.MISSING

    g = j.get("geo") or {}
    latitude = g.get("latitude")
    longitude = g.get("longitude")
    if not latitude:
        script = "".join(
            tree.xpath("//script[contains(text(), 'Drupal.settings')]/text()")
        )
        latitude = script.split('"lat":"')[1].split('"')[0]
        longitude = script.split('lon":"')[1].split('"')[0]

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="SA",
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
    session = SgRequests()
    locator_domain = "https://www.nandos.sa/"

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    }
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
