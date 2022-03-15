from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from concurrent import futures


def get_urls():
    r = session.get("https://www.humptys.com/locations/")
    tree = html.fromstring(r.text)

    return tree.xpath(
        "//li[contains(@class, 'current_page_item')]/following-sibling::li//a/@href"
    )


def get_data(page_url, sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    state = "".join(
        tree.xpath("//li[contains(@class,'current_page_item')]/a/text()")
    ).strip()
    cities = tree.xpath("//h3[./strong]|//h3")

    for c in cities:
        city = "".join(c.xpath("./strong/text()|./text()")).strip()
        tr = c.xpath("./following-sibling::table[1]//tr[./td]")
        for t in tr:
            street_address = "".join(t.xpath("./td[1]/text()")).strip()
            phone = "".join(t.xpath("./td[2]/text()")).strip()
            hours_of_operation = " ".join("".join(t.xpath("./td[3]/text()")).split())

            row = SgRecord(
                page_url=page_url,
                location_name="Humpty's Restaurant",
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=SgRecord.MISSING,
                country_code="CA",
                store_number=SgRecord.MISSING,
                phone=phone,
                location_type=SgRecord.MISSING,
                latitude=SgRecord.MISSING,
                longitude=SgRecord.MISSING,
                locator_domain=locator_domain,
                hours_of_operation=hours_of_operation,
            )

            sgw.write_row(row)


def fetch_data(sgw: SgWriter):
    urls = get_urls()

    with futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(get_data, url, sgw): url for url in urls}
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":
    locator_domain = "https://www.humptys.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
