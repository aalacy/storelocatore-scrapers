from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    page_url = "https://www.paul-singapore.com/location/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[contains(@id, 'row-') and .//h1]")

    for d in divs:
        location_name = "".join(d.xpath(".//h1/strong/text()")).strip()
        raw_address = "".join(
            d.xpath(".//h1[./strong]/following-sibling::*[1]/text()")
        ).strip()
        street_address = raw_address.split(", S(")[0]
        postal = raw_address.split(", S(")[-1].replace(")", "")
        phone = "".join(
            d.xpath(".//h1[./strong]/following-sibling::*[2]/text()")
        ).strip()
        if "/" in phone:
            phone = phone.split("/")[0].strip()

        hours = d.xpath(
            ".//*[contains(text(), 'hours')]/text()|.//*[contains(text(), 'hours')]/following-sibling::*//text()"
        )
        hours = list(filter(None, [h.strip() for h in hours]))
        if hours:
            hours.pop(0)
        hours_of_operation = ";".join(hours)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            zip_postal=postal,
            country_code="SG",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.paul-singapore.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
