from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.redlobster.com"
    api_url = "https://www.redlobster.com/international-franchises"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath(
        '//div[@class="accordion-content franchise-copy"]//p[./strong]/strong | //div[@class="accordion-content franchise-copy"]//p[./b]/b | //p[contains(text(), "7-8 Huis")]'
    )
    for d in div:

        page_url = "https://www.redlobster.com/international-franchises"
        location_name = "".join(d.xpath(".//text()")).replace("\n", "") or "<MISSING>"
        ad = d.xpath(".//following-sibling::text()")
        ad = list(filter(None, [a.strip() for a in ad]))
        try:
            adr = "".join(ad[0]).strip()
        except IndexError:
            adr = "<MISSING>"
        if location_name.find("7-8 Huis Ten Bosch Machi Sasebo") != -1:
            location_name = "<MISSING>"
            adr = "7-8 Huis Ten Bosch Machi Sasebo"
        if (
            adr.find("G/F 8 Cleveland") != -1
            or adr.find("Garden Pia Jetty West") != -1
            or adr.find("Daang Hari Road") != -1
            or adr.find("Level 1, S. Maison") != -1
            or adr.find("525 Av. Franklin") != -1
            or adr.find("Av. Cuauhtémoc No. 462,") != -1
        ):
            adr = " ".join(ad).strip()
        if adr.find("Tokyo Disney") != -1:
            adr = "".join(ad[1]).strip()
        if location_name == "Bayamón":
            adr = (
                "".join(d.xpath(".//following::div[1]/text()"))
                .replace("\n", "")
                .strip()
            )

        a = parse_address(International_Parser(), adr)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = (
            "".join(d.xpath(".//preceding::h2[1]/text()")).replace("\n", "").strip()
        )
        if country_code == "Japan":
            street_address = adr
        city = "".join(d.xpath(".//preceding::a[1]/text()")).replace("\n", "").strip()

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
            phone=SgRecord.MISSING,
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=SgRecord.MISSING,
            raw_address=adr,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
