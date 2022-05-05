from lxml import html
from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgpostal.sgpostal import International_Parser, parse_address


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.outsiders.co.il/"
    api_url = "https://www.outsiders.co.il/store-locator/"
    session = SgRequests()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    }
    r = session.get(api_url, headers=headers)
    tree = html.fromstring(r.text)
    div = tree.xpath('//dt[@class="locator__branch"]')
    for d in div:

        page_url = "https://www.outsiders.co.il/store-locator/"
        location_name = "".join(d.xpath(".//text()")).replace("\n", "").strip()
        ad = "".join(
            d.xpath(".//following-sibling::dd[1]//ul[1]//li[3]//text()")
        ).strip()
        a = parse_address(International_Parser(), ad)
        street_address = f"{a.street_address_1} {a.street_address_2}".replace(
            "None", ""
        ).strip()
        state = a.state or "<MISSING>"
        postal = a.postcode or "<MISSING>"
        country_code = "IL"
        city = a.city or "<MISSING>"
        phone = "".join(
            d.xpath(".//following-sibling::dd[1]//ul[1]//li[2]//text()")
        ).strip()
        hours_of_operation = (
            " ".join(
                d.xpath(
                    './/following::li[./span[text()="שעות פעילות:"]][1]/following-sibling::li//text()'
                )
            )
            .replace("\n", "")
            .replace(" :", "")
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.replace("ייתכנו שינויים בשעות הפעילות: ", "")
            .replace(" הבריאות.:", "")
            .replace("החנות פתוחה בהתאם להנחיות הממשלה ומשרד", "")
            .strip()
        )
        if hours_of_operation.find("יי") != -1:
            hours_of_operation = hours_of_operation.split("יי")[0].strip()

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
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        fetch_data(writer)
