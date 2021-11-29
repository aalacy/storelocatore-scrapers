from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address, International_Parser


def get_international(line):
    adr = parse_address(International_Parser(), line)
    city = adr.city
    state = adr.state
    postal = adr.postcode

    return city, state, postal


def fetch_data(sgw: SgWriter):
    page_url = "http://www.pinkberryjapan.com/stores/"
    r = session.get(page_url)
    tree = html.fromstring(r.text)
    divs = tree.xpath("//div[@class='location-data bg-pink']")

    for d in divs:
        location_name = "".join(d.xpath(".//h4//text()")).strip()
        phone = SgRecord.MISSING
        hours_of_operation = SgRecord.MISSING
        raw = []

        line = d.xpath("./text()")
        line = list(filter(None, [l.strip() for l in line]))
        for l in line:
            if "OPEN" in l:
                hours_of_operation = l
                break
            if l[0].isdigit():
                phone = l
                continue
            raw.append(l)

        street_address = raw.pop(0)
        raw_address = ", ".join(raw)
        city, state, postal = get_international(raw_address)

        row = SgRecord(
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code="JP",
            phone=phone,
            locator_domain=locator_domain,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    locator_domain = "http://www.pinkberryjapan.com/"
    session = SgRequests()
    with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
        fetch_data(writer)
