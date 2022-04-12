import re
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)

    divs = tree.xpath("//section[@class='co33-icon-text__content-wrap']")
    for d in divs:
        location_name = "".join(d.xpath(".//h2//text()")).strip()
        raw_address = "".join(
            d.xpath(".//b[contains(text(), 'Adresa')]/following-sibling::a[1]/text()")
        ).strip()
        street_address = raw_address.split(", ")[0]
        postal = re.findall(r"\d{3} \d{2}", raw_address).pop()
        city = raw_address.split(postal)[-1].strip()
        if city.startswith(","):
            city = city.replace(",", "").strip()
        if "-" in city:
            city = city.split("-")[-1].strip()
        if city[-1].isdigit():
            city = city.split()[0]
        phone = "".join(
            d.xpath(".//b[contains(text(), 'Telefon')]/following-sibling::text()[1]")
        ).strip()
        text = "".join(
            d.xpath(".//b[contains(text(), 'Adresa')]/following-sibling::a[1]/@href")
        )
        try:
            latitude, longitude = text.split("/@")[1].split(",")[:2]
        except IndexError:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = "".join(
            d.xpath(".//b[contains(text(), 'doba')]/following-sibling::text()[1]")
        ).strip()
        hours_of_operation = (
            hours_of_operation.replace("(", "").replace(")", "").strip()
        )

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code="CZ",
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.samsung.com/cz"
    page_url = "https://www.samsung.com/cz/znackoveprodejny/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
