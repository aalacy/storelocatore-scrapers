from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):
    api = "https://mcdonalds.md/products/locations/10?"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
    }
    r = session.get(api, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//table[@class='restaurant']")

    for d in divs:
        location_name = "".join(d.xpath(".//a/strong/text()")).strip()
        page_url = "".join(d.xpath(".//td/a/@href"))
        street_address = "".join(
            d.xpath(".//tr[./td/strong[contains(text(), 'Adresa')]]/td[2]/text()")
        ).strip()
        phone = "".join(
            d.xpath(".//tr[./td/strong[contains(text(), 'Telefon')]]/td[2]/text()")
        ).strip()
        if "," in phone:
            phone = phone.split(",")[0].strip()

        hours_of_operation = ";".join(
            d.xpath(".//tr[./td/strong[contains(text(), 'Orar')]]/td[2]/text()")
        ).strip()
        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=SgRecord.MISSING,
            state=SgRecord.MISSING,
            zip_postal=SgRecord.MISSING,
            country_code="MD",
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://mcdonalds.md/"
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        fetch_data(writer)
