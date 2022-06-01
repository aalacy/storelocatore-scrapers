import re
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


def get_coords(text):
    if "/@" in text:
        latitude, longitude = text.split("/@")[1].split(",")[:2]
    elif "&ll=" in text:
        latitude, longitude = text.split("&ll=")[1].split("&")[0].split(",")
    else:
        latitude, longitude = SgRecord.MISSING, SgRecord.MISSING

    return latitude, longitude


def fetch_data(sgw: SgWriter):
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath(
        "//div[contains(@class, 'sfContentBlock') and .//*[text()='Map']]"
    )

    for d in divs:
        lines = d.xpath(".//text()")
        lines = list(
            filter(
                None,
                [line.replace("\xa0", " ").replace("/", "").strip() for line in lines],
            )
        )

        location_name = lines.pop(0)
        raw_address = lines.pop(0)
        street_address, city, state, postal = get_international(raw_address)

        try:
            phone_text = "".join(d.xpath(".//text()"))
            phone = re.findall(r"\d{3}-\d{3}-\d{4}", phone_text)[0]
        except IndexError:
            phone = SgRecord.MISSING

        text = "".join(d.xpath(".//a/@href"))
        latitude, longitude = get_coords(text)

        hours_of_operation = SgRecord.MISSING
        if "Store Hours:" in lines:
            hours_of_operation = lines[lines.index("Store Hours:") + 1]

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="CA",
            latitude=latitude,
            longitude=longitude,
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "https://www.qualityfoods.com/"
    page_url = "https://www.qualityfoods.com/about-qf/location-hours"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
