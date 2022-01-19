from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.timhowan.com"
    api_url = "https://www.timhowan.com/our-stores/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//article[contains(@class, "single-outlet")]')
    for d in div:

        page_url = "https://www.timhowan.com/our-stores/"
        country_code = "".join(d.xpath(".//preceding::h3[1]/text()"))
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/p[contains(text(), "pm")]/text() | .//p[contains(text(), "PM")]/text()'
                )
            )
            .replace("\r\n", " ")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split()) or "<MISSING>"

        info = (
            " ".join(d.xpath(".//h5/following-sibling::p/text()"))
            .replace("\r\n", " ")
            .strip()
        )
        info = " ".join(info.split())

        location_name = "".join(d.xpath(".//h5/text()"))
        phone = "".join(d.xpath('.//p[contains(text(), "+")]/text()')) or "<MISSING>"
        if phone == "<MISSING>":
            phone = (
                "".join(d.xpath('.//p[contains(text(), "02-")]/text()')) or "<MISSING>"
            )
        if (
            country_code == "USA"
            and phone == "<MISSING>"
            or country_code == "China"
            and phone == "<MISSING>"
        ):
            phone = (
                "".join(d.xpath(".//h5/following-sibling::p[2]/text()")) or "<MISSING>"
            )
        if country_code == "Philippines" and phone == "<MISSING>":
            phone = (
                "".join(d.xpath('.//p[contains(text(), "(02)")]/text()')) or "<MISSING>"
            )
        if country_code == "Taiwan" and phone == "<MISSING>":
            phone = (
                "".join(d.xpath('.//p[contains(text(), "-")]/text()')) or "<MISSING>"
            )
        ad = info
        ad = " ".join(ad.split()).replace(f"{phone}", "")
        if ad.find(f"{hours_of_operation}") != -1 and hours_of_operation != "<MISSING>":
            ad = ad.split(f"{hours_of_operation}")[1].strip()

        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        if state == "Sar":
            state = "<MISSING>"
        postal = a.postcode or "<MISSING>"
        if country_code == "Singapore":
            postal = ad.split("S(")[1].split(")")[0].strip()
        if postal == "B1M-1":
            postal = "<MISSING>"
        city = a.city or "<MISSING>"
        if city == "City S" or city == "Sar":
            city = "<MISSING>"
        if city.find("Barangay 76") != -1:
            city = city.replace("Barangay 76", "").strip()

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
            location_type=SgRecord.MISSING,
            latitude=SgRecord.MISSING,
            longitude=SgRecord.MISSING,
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
