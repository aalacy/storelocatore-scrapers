from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.jamesallen.com"
    page_url = "https://www.jamesallen.com/locations/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(page_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath("//div[./h3]")
    for d in div:

        location_name = "".join(d.xpath(".//h3/text()"))
        if location_name == "Customer information":
            continue
        info = (
            " ".join(d.xpath(".//h3/following-sibling::div[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        ad = info.replace("By appointment only!", "").strip()
        if ad.find("Open") != -1:
            ad = ad.split("Open")[0].strip()
        a = parse_address(International_Parser(), ad)
        street_address = (
            f"{a.street_address_1} {a.street_address_2}".replace("None", "").strip()
            or "<MISSING>"
        )
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        hours_of_operation = "<MISSING>"
        if info.find("Open") != -1:
            hours_of_operation = info.split("Open:")[1].strip()
        phone = (
            "".join(
                d.xpath(
                    './/h3/following-sibling::div[contains(text(), "Contact Customer")]/text()'
                )
            )
            .split("at")[1]
            .split()[0]
            .strip()
        )

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
