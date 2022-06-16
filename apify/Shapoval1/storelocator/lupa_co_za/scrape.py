from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.lupa.co.za/"
    page_url = "https://www.lupa.co.za/hours-locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[contains(@class,"elementor-column elementor-col-50")]')
    for d in div:

        location_name = (
            "".join(d.xpath(".//iframe/following::h2[1]//text()"))
            .replace("\n", "")
            .strip()
        )
        if not location_name:
            continue
        ad = (
            " ".join(d.xpath(".//iframe/following::p[1]//text()"))
            .replace("\n", "")
            .strip()
        )
        ad = " ".join(ad.split())
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "ZA"
        city = a.city or "<MISSING>"
        phone = (
            "".join(
                d.xpath(
                    './/a[contains(@href, "tel")]//text() | .//a[contains(@href, "http")]//text()'
                )
            )
            or "<MISSING>"
        )
        if phone.find("/") != -1:
            phone = phone.split("/")[0].strip()
        hours_of_operation = (
            " ".join(d.xpath('.//h2[text()="Hours"]/following::div[./p][1]//text()'))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = " ".join(hours_of_operation.split())

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
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
