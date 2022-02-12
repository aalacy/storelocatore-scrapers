from sgscrape.sgpostal import International_Parser, parse_address
from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    page_url = "https://qwenchjuice.com/locations"
    session = SgRequests()

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="location-block "]')
    for b in block:
        location_name = "".join(b.xpath(".//h3/text()"))
        ad = "".join(b.xpath(".//p[2]/text()"))
        a = parse_address(International_Parser(), ad)

        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        phone = "".join(b.xpath(".//p[1]/text()")).replace("P:", "").strip()
        if phone == "TBD":
            phone = "<MISSING>"
        city = a.city or "<MISSING>"
        if street_address == "32 5Th Ave.":
            city = "Brooklyn"

        postal = a.postcode or "<MISSING>"
        state = a.state or "<MISSING>"
        country_code = "CA"
        if postal.isdigit():
            country_code = "US"

        location_type = "<MISSING>"
        cms = "".join(
            b.xpath('.//preceding::h2[contains(text(), "Coming Soon")][1]/text()')
        )
        if cms:
            location_type = "Coming Soon"
        tcls = "".join(
            b.xpath('.//preceding::h2[1]/span[contains(text(), "Temporarily")]/text()')
        )
        if tcls:
            location_type = "Temporarily Closed"

        row = SgRecord(
            locator_domain=locator_domain,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address,
            city=city,
            state=state,
            zip_postal=postal,
            country_code=country_code,
            store_number=SgRecord.MISSING,
            phone=phone,
            location_type=location_type,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://qwenchjuice.com/"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
