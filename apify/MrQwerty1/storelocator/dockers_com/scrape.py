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
    postal = adr.postcode or SgRecord.MISSING

    return street, city, postal


def get_cz(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city
    postal = adr.postcode

    return city, postal


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='store-finder__store']")

    for d in divs:
        location_name = "".join(d.xpath(".//h2//text()")).strip()
        raw_address = " ".join(
            " ".join(
                d.xpath(".//p[contains(text(), 'Address')]/following-sibling::p/text()")
            ).split()
        )
        line = d.xpath(".//p[contains(text(), 'Address')]/following-sibling::p/text()")
        if len(line) == 1:
            street_address, city, postal = get_international(raw_address)
        else:
            street_address = line.pop(0)
            city, postal = get_cz(line.pop())
        phone = "".join(
            d.xpath(".//p[contains(text(), 'Phone')]/following-sibling::text()")
        ).strip()
        text = "".join(d.xpath(".//a[contains(text(), 'Directions')]/@href")).replace(
            "://", ""
        )
        if "//" in text:
            latitude, longitude = text.split("//")[1].split(",")[:2]
        else:
            latitude, longitude = SgRecord.MISSING, SgRecord.MISSING
        hours_of_operation = " ".join(
            ";".join(
                d.xpath(".//p[contains(text(), 'Hours')]/following-sibling::p/text()")
            ).split()
        )
        country = "".join(d.xpath("./@data-store")).capitalize()

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            zip_postal=postal,
            country_code=country,
            phone=phone,
            latitude=latitude,
            longitude=longitude,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://dockers.com/"
    page_url = "https://eu.dockers.com/pages/find-a-store"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
