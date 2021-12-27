from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://paul.kz/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='contact-item']")

    for d in divs:
        location_name = "".join(d.xpath(".//div[@class='contact-name']/text()")).strip()
        raw_address = "".join(d.xpath(".//div[@class='contact-adress']/text()")).strip()
        city = raw_address.split(", ")[0].replace("г.", "").strip()
        street_address = ", ".join(raw_address.split(", ")[1:])
        phone = "".join(d.xpath(".//div[@class='contact-phone']/a/text()")).strip()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            country_code="KZ",
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://paul.kz/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
