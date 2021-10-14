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
    r = session.get("https://www.tkmaxx.nl/winkel-zoeken")
    tree = html.fromstring(r.text)
    text = "".join(tree.xpath("//script[contains(text(), 'markers')]/text()"))
    text = text.split('"markers":')[1].split("],")[0] + "]"
    js = json.loads(text)
    for j in js:
        source = j.get("text")
        root = html.fromstring(source)
        urls.append("".join(root.xpath("//a/@href")))

    return urls


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.tkmaxx.nl{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    try:
        d = tree.xpath("//div[@class='nearby-store active-store']")[0]
    except IndexError:
        return

    location_name = "".join(d.xpath("./a/text()")).strip()
    store_number = "".join(d.xpath("./@data-store-id"))
    latitude = "".join(d.xpath("./@data-latitude"))
    longitude = "".join(d.xpath("./@data-longitude"))
    b = d.xpath("./following-sibling::div[1]")[0]
    street_address = "".join(b.xpath(".//p[@itemprop='streetAddress']/text()")).strip()
    city = "".join(b.xpath(".//p[@itemprop='addressLocality']/text()")).strip() or " "
    if city == " ":
        city = location_name.replace("TK Maxx ", "")
        if "(" in city:
            city = city.split("(")[0].strip()
    postal = "".join(b.xpath(".//p[@itemprop='zipCode']/text()")).strip()
    phone = "".join(b.xpath(".//p[@itemprop='telephone']/text()")).strip()
    try:
        hours_of_operation = b.xpath(".//span[@itemprop='openingHours']/text()")[
            0
        ].strip()
    except IndexError:
        hours_of_operation = SgRecord.MISSING

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=postal,
        country_code="NL",
        store_number=store_number,
        phone=phone,
        location_type=SgRecord.MISSING,
        latitude=latitude,
        longitude=longitude,
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
    locator_domain = "https://www.tkmaxx.nl/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
