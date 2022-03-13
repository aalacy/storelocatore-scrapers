from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures
from sgscrape.sgpostal import parse_address, International_Parser


def get_urls():
    r = session.get("https://www.freshstmarket.com/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//div[text()='Select a Location']/following-sibling::ul/li[not(@class)]/a/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    location_name = "".join(tree.xpath("//title/text()")).split("-")[0].strip()
    line = "".join(tree.xpath("//div[contains(@class, 'cAddress')]//text()")).strip()

    adr = parse_address(International_Parser(), line)
    street_address = f"{adr.street_address_1} {adr.street_address_2 or ''}".replace(
        "None", ""
    ).strip()
    city = adr.city
    state = adr.state
    postal = adr.postcode
    phone = "".join(tree.xpath("//div[contains(@class, 'phone ')]/i[1]/text()")).strip()
    hours = tree.xpath("//address//div[contains(@class,'time cTime')]/p/text()")
    hours = list(
        filter(None, [h.replace("(", "").replace(")", "").strip() for h in hours])
    )
    hours_of_operation = ";".join(hours)
    if ";;" in hours_of_operation:
        hours_of_operation = hours_of_operation.split(";;")[0]

    row = SgRecord(
        page_url=page_url,
        location_name=location_name,
        street_address=street_address,
        city=city,
        state=state,
        zip_postal=postal,
        country_code="CA",
        phone=phone,
        locator_domain=locator_domain,
        hours_of_operation=hours_of_operation,
    )

    sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.freshstmarket.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
