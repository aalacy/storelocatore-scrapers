from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds


def fetch_data(sgw: SgWriter):
    api = "https://doscoyotes.com/all-locations/"
    r = session.get(api)
    tree = html.fromstring(r.text)

    divs = tree.xpath(
        "//div[contains(@class, 'elementor-column elementor-col-33') and .//span[contains(text(), 'See More')]]"
    )
    for d in divs:
        line = d.xpath(".//div//text()")
        line = list(filter(None, [l.strip() for l in line]))

        location_name = line.pop(0)
        page_url = "".join(
            d.xpath(".//a[contains(@class, 'elementor-button-link')]/@href")
        )
        street_address = line.pop(0)
        if street_address.endswith(","):
            street_address = street_address[:-1]
        csz = line.pop(0)
        city = csz.split(",")[0].strip()
        csz = csz.split(",")[1].strip()
        state, postal = csz.split()
        phone = line.pop(0).replace("Phone:", "").strip()
        hours_of_operation = " ".join(
            ";".join(line[: line.index("View on Map")]).split()
        )
        if "Temporarily" in hours_of_operation:
            hours_of_operation = "Temporarily Closed"

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
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://doscoyotes.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
