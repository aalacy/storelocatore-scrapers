from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import USA_Best_Parser, parse_address


def fetch_data(sgw: SgWriter):

    api_url = "https://www.hsn.com/content/HSN_Outlet/261#"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//h3[@class="_38821_h3"]')
    for d in div:

        page_url = "https://www.hsn.com/content/HSN_Outlet/261#"
        location_name = "".join(d.xpath(".//text()"))

        location_type = "outlet"
        ad = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[1]"))
            .replace("\n", "")
            .strip()
        )

        if location_name == "HSN Retail Outlet of Bardmoor":
            ad = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
                .replace("\n", "")
                .strip()
            )

        a = parse_address(USA_Best_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "US"
        city = a.city or "<MISSING>"
        phone = (
            "".join(d.xpath(".//following-sibling::p[1]/text()[2]"))
            .replace("\n", "")
            .strip()
        )
        if location_name == "HSN Retail Outlet of Bardmoor":
            phone = (
                "".join(d.xpath(".//following-sibling::p[1]/text()[3]"))
                .replace("\n", "")
                .strip()
            )
        hours_of_operation = (
            " ".join(d.xpath(".//following-sibling::p[1]/text()"))
            .replace("\n", "")
            .strip()
        )
        hours_of_operation = hours_of_operation.split("Hours of Operation:")[1].strip()
        if hours_of_operation.find("and") != -1:
            hours_of_operation = hours_of_operation.split("and")[0].strip()

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
            hours_of_operation=hours_of_operation,
            raw_address=ad,
        )

        sgw.write_row(row)


if __name__ == "__main__":
    session = SgRequests()
    locator_domain = "https://www.hsn.com"
    with SgWriter(
        SgRecordDeduper(SgRecordID({SgRecord.Headers.RAW_ADDRESS}))
    ) as writer:
        fetch_data(writer)
