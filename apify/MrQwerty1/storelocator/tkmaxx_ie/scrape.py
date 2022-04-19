from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.tkmaxx.ie/sitemap")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//a[@class='top-right-store-locator-link']/following-sibling::ul//a/@href"
    )


def get_data(slug, sgw: SgWriter):
    page_url = f"https://www.tkmaxx.ie{slug}"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    d = tree.xpath("//div[@class='nearby-store active-store']")[0]

    location_name = "".join(d.xpath("./a/text()")).strip()
    page_url = "https://www.tkmaxx.ie" + "".join(d.xpath("./a/@href"))
    store_number = "".join(d.xpath("./@data-store-id"))
    latitude = "".join(d.xpath("./@data-latitude"))
    longitude = "".join(d.xpath("./@data-longitude"))
    b = d.xpath("./following-sibling::div[1]")[0]
    street_address = "".join(b.xpath(".//p[@itemprop='streetAddress']/text()")).strip()
    city = "".join(b.xpath(".//p[@itemprop='addressLocality']/text()")).strip()
    if not city:
        city = location_name
    if city[0].isdigit():
        street_address = city
        city = location_name
    postal = "".join(b.xpath(".//p[@itemprop='zipCode']/text()")).strip()
    phone = "".join(b.xpath(".//p[@itemprop='telephone']/text()")).strip()
    hours_of_operation = "".join(
        b.xpath(".//span[@itemprop='openingHours']/text()")
    ).strip()
    if "Bank" in hours_of_operation:
        hours_of_operation = hours_of_operation.split("Bank")[0].strip()

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=SgRecord.MISSING,
        zip_postal=postal,
        country_code="IE",
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

    with futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.tkmaxx.ie/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
