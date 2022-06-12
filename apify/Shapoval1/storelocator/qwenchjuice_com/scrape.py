from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    page_url = "https://qwenchjuice.com/locations"

    r = session.get(page_url)
    tree = html.fromstring(r.text)
    block = tree.xpath('//div[@class="location-block "]')
    for b in block:
        location_name = "".join(b.xpath(".//h3/text()"))
        info = b.xpath(".//h3/following-sibling::p//text()")
        info = list(filter(None, [a.strip() for a in info]))
        adr = " ".join(info)
        phone = "<MISSING>"
        for i in info:
            if "P:" in i:
                phone = "".join(i).replace("P:", "").strip()
        if phone == "TBD":
            phone = "<MISSING>"
        if adr.find(f"{phone}") != -1:
            adr = adr.split(f"{phone}")[1].strip()
        if adr.count("TBD") > 1:
            adr = "<MISSING>"
        if adr.find("TBD") != -1:
            adr = adr.split("TBD")[1].strip()

        street_address = "<MISSING>"
        city = "<MISSING>"
        postal = "<MISSING>"
        state = "<MISSING>"
        country_code = "CA"
        if adr != "<MISSING>":
            a = parse_address(International_Parser(), adr)
            street_address = f"{a.street_address_1} {a.street_address_2}".replace(
                "None", ""
            ).strip()
            state = a.state or "<MISSING>"
            postal = a.postcode or "<MISSING>"
            country_code = "CA"
            city = a.city or "<MISSING>"
        if postal.isdigit():
            country_code = "US"
        if location_name == "Brooklyn":
            city = "Brooklyn"
        location_type = "<MISSING>"
        title = "".join(b.xpath(".//preceding::h2[1]//text()"))
        if title.find("Temporarily Closed") != -1:
            location_type = "Temporarily Closed"
        if title.find("Coming Soon") != -1:
            location_type = "Coming Soon"

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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://qwenchjuice.com/"
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.PHONE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
