from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[./a[contains(@href, 'google')]]")

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(filter(None, [line.strip() for line in lines]))
        location_name = lines.pop(0)
        adr = lines[: lines.index("Store hours")]
        hours_of_operation = ";".join(lines[lines.index("Store hours") + 1 :])
        csz = adr.pop()
        street_address = adr.pop()
        city = csz.split(", ")[0]
        csz = csz.split(", ")[1]
        state, postal = csz.split()

        text = "".join(d.xpath(".//a/@href"))
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        if "/@" in text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="US",
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://amazon.com/fresh"
    page_url = "https://www.amazon.com/fmc/m/20190651?almBrandId=QW1hem9uIEZyZXNo"
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.LOCATION_NAME}))
    ) as writer:
        fetch_data(writer)
