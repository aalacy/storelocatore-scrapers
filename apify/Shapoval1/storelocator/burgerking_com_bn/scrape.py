from lxml import html
from sgscrape.sgpostal import International_Parser, parse_address
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.burgerking.com.bn"
    api_url = "https://www.burgerking.com.bn/contact-us"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//div[./strong[not(contains(text(), "Hours"))]]')
    for d in div:

        page_url = "https://www.burgerking.com.bn/contact-us"
        location_name = "".join(d.xpath(".//strong/text()"))
        ad = " ".join(d.xpath(".//following::div[1]//text()")).replace("\n", "").strip()
        adr = ad
        if adr.find("Tel") != -1:
            adr = adr.split("Tel")[0].strip()
        a = parse_address(International_Parser(), adr)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "Brunei"
        city = a.city or "<MISSING>"
        phone = "<MISSING>"
        if ad.find("Tel") != -1:
            phone = ad.split("Tel:")[1].strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::div[contains(text(), "Monday - Sunday")][1]/text()'
                )
            )
            .replace("\n", "")
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
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        fetch_data(writer)
