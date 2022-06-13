from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    adr1 = adr.street_address_1 or ""
    adr2 = adr.street_address_2 or ""
    street = f"{adr1} {adr2}".strip()
    city = adr.city or SgRecord.MISSING
    state = adr.state or SgRecord.MISSING
    postal = adr.postcode or SgRecord.MISSING

    return street, city, state, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='two_col-grid-content']")

    for d in divs:
        location_name = "".join(
            d.xpath(".//div[@class='bobbi-store__name']/text()")
        ).strip()
        raw_address = "".join(
            d.xpath(".//div[@class='bobbi-store__address']//text()")
        ).strip()
        phone = "".join(d.xpath(".//a[contains(@href, 'tel:')]/text()")).strip()
        street_address, city, state, postal = get_international(raw_address)
        postal = postal.replace("CP", "").strip()
        country_code = "MX"

        text = "".join(d.xpath(".//a[contains(@href, '/@')]/@href"))
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        if text:
            latitude, longitude = text.split("/@")[1].split(",")[:2]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.bobbibrown.com.mx/"
    page_url = "https://www.bobbibrown.com.mx/store_locator"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:97.0) Gecko/20100101 Firefox/97.0",
    }
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
